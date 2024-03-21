#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2023

from typing import Dict, List
from analysing_tools.constants.referee_decisions import EnumRefereeDecision
# from UploadToServer import UploadToServer
import json
import os


def create_old_json(teams: Dict[str, str], ball_on_sides: Dict[str, float], possessions: Dict[str, float],
                    shots: Dict[str, List[int]], referee_decisions: Dict[EnumRefereeDecision, List[int]],
                    tackles: Dict[str, List[int]], goals: Dict[str, List[int]],
                    passes: Dict[str, int], pass_chains: Dict[str, Dict[int, int]], holes: Dict[str, List[int]],
                    commit_id: str, logFileName: str, matchUpTeamNameL: str, matchUpTeamNameR: str, protocol_id: str) -> str:
    team_left_name = teams["team_l"]
    team_right_name = teams["team_r"]
    stream = os.popen('hostname')
    hostname = stream.read().strip()

    json_dict = {
        "logFileName": logFileName,
        "commitID": commit_id,
        "protocolID": protocol_id,
        "hostname": hostname,
        "team_l":  team_left_name,
        "team_r":  team_right_name,
        "matchUp_team_l": matchUpTeamNameL,
        "matchUp_team_r": matchUpTeamNameR,
        "ball_on_side_l":   round(ball_on_sides[team_left_name]),
        "ball_on_side_r":   round(ball_on_sides[team_right_name]),
        "possession_l":     round(possessions[team_left_name]),
        "possession_r":     round(possessions[team_right_name]),
        "total_shots_l":    shots[team_left_name][1],
        "total_shots_r":    shots[team_right_name][1],
        "shots_on_target_l":    shots[team_left_name][0],
        "shots_on_target_r":    shots[team_right_name][0],
        "free_kicks_l":     referee_decisions[EnumRefereeDecision.FREE_KICK_L],
        "free_kicks_r":     referee_decisions[EnumRefereeDecision.FREE_KICK_R],
        "corners_l":        referee_decisions[EnumRefereeDecision.CORNER_KICK_L],
        "corners_r":        referee_decisions[EnumRefereeDecision.CORNER_KICK_R],
        "offsides_l":       referee_decisions[EnumRefereeDecision.OFFSIDE_L],
        "offsides_r":       referee_decisions[EnumRefereeDecision.OFFSIDE_R],
        "tackles_l":        tackles[team_left_name],
        "tackles_r":        tackles[team_right_name],
        "fouls_l":  referee_decisions[EnumRefereeDecision.FOUL_CHARGE_L],
        "fouls_r":  referee_decisions[EnumRefereeDecision.FOUL_CHARGE_R],
        "yellow_cards_l":   referee_decisions[EnumRefereeDecision.YELLOW_CARD_L],
        "yellow_cards_r":   referee_decisions[EnumRefereeDecision.YELLOW_CARD_R],
        "red_cards_l":      referee_decisions[EnumRefereeDecision.RED_CARD_L],
        "red_cards_r":      referee_decisions[EnumRefereeDecision.RED_CARD_R],
        "goals_l":  goals[team_left_name],
        "goals_r":  goals[team_right_name],
        "passes_l": passes[team_left_name],
        "passes_r": passes[team_right_name],
        "pass_chains_l":    transform_pass_chains_to_list(pass_chains[team_left_name]),
        "pass_chains_r":    transform_pass_chains_to_list(pass_chains[team_right_name]),
        "holes_l": holes[team_left_name],
        "holes_r": holes[team_right_name],
    }

    # return json.dumps(json_dict)
    return json_dict


def transform_pass_chains_to_list(pass_chains: Dict[int, int], *, min_chain_length=2) -> List[int]:
    """
    transform a dict pass chain into a list pass chain
    :param pass_chains: the pass chains in dict format
    :return: a list with length=maximum pass_chain length -(min_chain_length -1), the values of the list are the corresponding occurrences
    with index=pass chain length -min_chain_length
    """
    # initialize dict
    transformed_chain = [0 for _ in range(max(pass_chains.keys()) - (min_chain_length-1))]

    for chain_length, amount in pass_chains.items():
        # set the values that aren't zero
        # -min_chain_length because min_chain_length is the smallest length at index 0
        transformed_chain[chain_length-min_chain_length] = amount

    return transformed_chain
