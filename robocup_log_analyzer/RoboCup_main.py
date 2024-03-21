#!/usr/bin/python3
#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2023

import glob
import os
import sys
import shutil
from pathlib import Path
from random import randint

import yaml

# XXX: Debug print file
DEBUG_FILE = "/tmp/robocup/empty"
# XXX: Debug create tmp folder
if not os.path.exists("/tmp/robocup/"):
    os.makedirs("/tmp/robocup/")
# XXX: Debug print
with open(DEBUG_FILE, 'a+') as debug_file:
    debug_file.write("Python version: " + str(sys.version) + '\n')

from typing import Tuple
from analysing_tools.datamodel.datamodel import Game
from analysing_tools.parser import parser
from analysing_tools.extraction import player_reformat, kick_filter, ball_reformat, referee_reformat
from analysing_tools.analysis import analyzer, passes, time_out

import json_handler
import UploadToServer

TEMP_LOGS_FOLDER = "/tmp/robocup/logs"


def main():
    # XXX: Debug print
    with open(DEBUG_FILE, 'a+') as file:
        file.write("***** Parsing Command line parameters *****\n")
    path = get_rcl_rcg_log_path()
    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("***** Parsing log files/Creating datamodel *****\n")
    
    datamodel = create_datamodel(path[1], path[0])
    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("***** Analysing game *****\n")
    analyse(datamodel, path[1], path[0])


def get_rcl_rcg_log_path():
    path = sys.argv[1]
    # os.chdir(path)

    rcg_log_path = ''
    rcl_log_path = ''

    if not path.endswith("/"):
        path = path + "/"
    for sFile in glob.glob(path + "*.rcg"):
        rcg_log_path = sFile
        rcl_log_path = glob.glob(sFile[:-len(".rcg")]+".rcl")[0]

    ## We salt the log files to make sure that file names are unique across all
    ## computers. Timestamp already does that but I'm paranoid.
    # randomSuffix = str(randint(100, 999))
    # print(randomSuffix)
    # salted_rcg_path = Path(rcg_log_path).stem + "-" + randomSuffix + ".rcg"
    # salted_rcl_path = Path(rcl_log_path).stem + "-" + randomSuffix + ".rcl"

    # print("rename rcg ", rcg_log_path)
    # os.rename(rcg_log_path, salted_rcg_path)
    # print("rename rcl ", rcl_log_path)
    # os.rename(rcl_log_path, salted_rcl_path)

    # return salted_rcg_path, salted_rcl_path
    return rcg_log_path, rcl_log_path

    
def create_datamodel(rcl_path: str, rcg_path: str) -> Game:
    return parser(rcg_path, rcl_path)


def analyse(game: Game, rcl_log_path, rcg_log_path):
    print("********** Reformatting data **********")
    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("\t***** Reformatting data *****\n")
    ordered_players = player_reformat.get_player_list_ordered_by_time(game.players)
    reformated_balls = ball_reformat.get_ball_list_ordered_by_time(game.balls)
    decision_dict = referee_reformat.get_referee_decision_as_playtime_dict(game.referee_decisions)
    successful_kicks_tackles = kick_filter.get_successful_kicks_tackles(game.kicks, game.tackles, ordered_players[1],
                                                                        game.team_l, game.team_r)

    successful_kicks = kick_filter.get_successful_kicks(game.kicks, ordered_players[1], game.team_l, game.team_r)
    single_successful_kicks = kick_filter.get_singular_kicks(successful_kicks)
    successful_tackles = kick_filter.get_successful_tackles(game.tackles, ordered_players[1], game.team_l, game.team_r)
    single_successful_tackles = kick_filter.get_singular_tackles(successful_tackles)

    print("********** Analysing Data ************")
    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("\t***** Analysing data *****\n")
    tackles = analyzer.get_tackle_times(game.tackles, game.team_l, game.team_r)
    field_half_ratio = analyzer.analyze_ball_field_half_ratio(game.balls, game.team_l, game.team_r)
    ref_dec_timesteps = analyzer.get_referee_decision_timestemps(game.referee_decisions, game.team_l, game.team_r)
    possession_ratio = analyzer.analyze_possession_percentage(game.referee_decisions, successful_kicks_tackles[1],
                                                              game.team_l, game.team_r)
    shots = analyzer.analyse_shot(game.kicks, game.balls, game.team_l, game.team_r)
    goals = analyzer.get_goals_per_half_and_timing(game.referee_decisions, game.team_l, game.team_r)
    pass_count = passes.count_passes(successful_kicks_tackles[1], reformated_balls[0], decision_dict,
                                     game.team_l, game.team_r)
    pass_chains = passes.pass_chain(single_successful_kicks, single_successful_tackles, game.team_l, game.team_r)

    pass_count_sum = {game.team_l: sum(pass_count[game.team_l].values()),
                      game.team_r: sum(pass_count[game.team_r].values())}

    goal_timings = {game.team_l: goals[game.team_l][-1],
                    game.team_r: goals[game.team_r][-1]}

    holeEvents = game.kicks
    holeEvents.extend(game.dashes)
    holeEvents.extend(game.tackles)
    holeEvents.extend(game.turns)

    holes = time_out.find_delayed_messages(holeEvents, game.team_l, game.team_r)

    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("\t***** Retrieving commit id *****\n")
    commit_id = UploadToServer.get_commit_id()
    protocol_id = UploadToServer.get_protocol_id()

    # Extracting the log file name from path
    logFileName = Path(rcl_log_path).stem

    matchUpTeamNameL, matchUpTeamNameR = grabMatchUpNames()

    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("\t***** Creating json *****\n")
    result_json = json_handler.create_old_json(teams={'team_l': game.team_l, 'team_r': game.team_r},
                                               ball_on_sides=field_half_ratio,
                                               possessions=possession_ratio, shots=shots,
                                               referee_decisions=ref_dec_timesteps, tackles=tackles, goals=goal_timings,
                                               passes=pass_count_sum, pass_chains=pass_chains, holes=holes,
                                               commit_id=commit_id, logFileName=logFileName, matchUpTeamNameL=matchUpTeamNameL,
                                               matchUpTeamNameR=matchUpTeamNameR, protocol_id=protocol_id)

    print("createJsonData: ", result_json)

    # XXX: Debug print
    with open(DEBUG_FILE, 'a') as file:
        file.write("\t***** Uploading Json *****\n")
    # push to server and retrieve new match id
    match_id = UploadToServer.push_to_server(jsonData=result_json, commit_id=commit_id)

    shutil.move(rcg_log_path, TEMP_LOGS_FOLDER)
    shutil.move(rcl_log_path, TEMP_LOGS_FOLDER)

# This is quite a fragile way of doing things, as there are no real rules to matchup team names.
# The will produce the wrong names if for instance a team has the name "Team-vs-the-world" 
# Because we look for the -vs- string to split team l and r.
def grabMatchUpNames():
    pathToMatchYaml = os.path.join(sys.argv[1], "match.yml")
    with open(pathToMatchYaml, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    
    teamLFolderPath = data["team_l"]["team_dir"]
    teamRFolderPath = data["team_r"]["team_dir"]

    lastSlashIndexL = len(teamLFolderPath) - teamLFolderPath[::-1].index("/")
    lastSlashIndexR = len(teamRFolderPath) - teamRFolderPath[::-1].index("/")

    matchUpNameL = teamLFolderPath[lastSlashIndexL:]
    matchUpNameR = teamRFolderPath[lastSlashIndexR:]

    return matchUpNameL, matchUpNameR

if __name__ == "__main__":
    main()
