#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2023
import sys

from analysing_tools.analysis import analyzer, passes, stamina, time_out
from analysing_tools.extraction import player_reformat, kick_filter, ball_reformat, referee_reformat
from analysing_tools.parser import parser
import json_handler


def main():
    if len(sys.argv) < 2:
        print("specify base name of rcg/rcl file")
        exit(0)
    rcg_file = sys.argv[1] + ".rcg"
    rcl_file = sys.argv[1] + ".rcl"
    datamodel = parser(rcg_file, rcl_file)

    print("finished parsing")
    rcg = rcl = game = datamodel
    ordered_players = player_reformat.get_player_list_ordered_by_time(rcg.players)
    reformated_balls = ball_reformat.get_ball_list_ordered_by_time(rcg.balls)
    decision_dict = referee_reformat.get_referee_decision_as_playtime_dict(rcl.referee_decisions)

    successful_kicks_tackles = kick_filter.get_successful_kicks_tackles(rcl.kicks, rcl.tackles, ordered_players[1],
                                                                        rcg.team_l, rcg.team_r)

    successful_kicks = kick_filter.get_successful_kicks(game.kicks, ordered_players[1], game.team_l, game.team_r)
    single_successful_kicks = kick_filter.get_singular_kicks(successful_kicks)
    successful_tackles = kick_filter.get_successful_tackles(game.tackles, ordered_players[1], game.team_l, game.team_r)
    single_successful_tackles = kick_filter.get_singular_tackles(successful_tackles)

    print("finished filtering")

    print(f"tackles: {analyzer.get_tackle_times(rcl.tackles, rcg.team_l, rcg.team_r)}")
    print(f"ball field half: {analyzer.analyze_ball_field_half_ratio(rcg.balls, rcg.team_l, rcg.team_r)}")
    print(f"count referee decision: {analyzer.count_referee_decisions(rcl.referee_decisions, rcg.team_l, rcg.team_r)}")
    print(f"referee decision timestemps: {analyzer.get_referee_decision_timestemps(rcl.referee_decisions, rcg.team_l, rcg.team_r)}")
    print(f"possesion percentage: {analyzer.analyze_possession_percentage(rcl.referee_decisions, successful_kicks_tackles[1], rcg.team_l, rcg.team_r)}")
    print(f"count passes: {analyzer.count_passes_and_missed_passes(rcl.kicks, rcg.team_l, rcg.team_r)}")
    print(f"count dribblings: {analyzer.count_successful_and_unsuccessful_dribblings(rcl.kicks, rcg.team_l, rcg.team_r)}")
    print(f"goals per half: {analyzer.get_goals_per_half_and_timing(rcl.referee_decisions, rcg.team_l, rcg.team_r)}")
    print(f"shot: {analyzer.analyse_shot(rcl.kicks, rcg.balls, rcg.team_l, rcg.team_r)}")
    #
    print(f"log3 passes: {passes.count_passes(successful_kicks_tackles[1], reformated_balls[0], decision_dict, rcg.team_l, rcg.team_r)}")

    pass_chains = passes.pass_chain(single_successful_kicks, single_successful_tackles, game.team_l, game.team_r)

    print(f"pass chains: {pass_chains}")
    print(f"list pass chain L: {json_handler.transform_pass_chains_to_list(pass_chains[game.team_l])}")
    print(f"list pass chain R: {json_handler.transform_pass_chains_to_list(pass_chains[game.team_r])}")

    stamina_usage = stamina.get_stamina_usage_by_distance_per_player(ordered_players[0], reformated_balls[0],
                                                                     game.team_l, game.team_r,
                                                                     distance_classes=[5.0, 10.0, 15.0, 25.0, 35.0, 50.0, 60.0])
    print(f"stamina usage ball distance: {stamina_usage}")

    events = rcl.kicks
    events.extend(rcl.dashes)
    events.extend(rcl.tackles)
    events.extend(rcl.turns)
    holes = time_out.find_delayed_messages(events, rcg.team_l, rcg.team_r)
    print(f"(black) holes: {holes}")


if __name__ == '__main__':
    main()
