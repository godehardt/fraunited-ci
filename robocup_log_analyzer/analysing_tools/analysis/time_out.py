from typing import List, Dict, Union
from ..datamodel.datamodel import Kick, Tackle, Dash, Turn


# TODO: UNFINISHED
def find_delayed_messages(events: List[Union[Kick, Tackle, Dash, Turn]],
                          team_left_name: str, team_right_name: str) -> Dict[str, List[int]]:
    """
    This function analyses when a command is not send on time to the server
    Hole:
    Black hole:

    :param events: a list of all events (Kick, Tackle, Dash, Turn)
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team

    :return: Map from team to an array, containing the timestamps of holes
    """
    # left_team_actions = [0] * 6000
    # right_team_actions = [0] * 6000
    left_team_actions = [[0] * 11 for i in range(6001)]
    right_team_actions = [[0] * 11 for i in range(6001)]
    holes = {team_left_name: [],
             team_right_name: []}

    # print("find delayed messages")
    for e in events:
        # print(e.time_info.playtime)
        # print("   " + str(e.player_number))
        if e.team_name == team_left_name:
            left_team_actions[e.time_info.playtime][e.player_number - 1] += 1
        #            print(str(e.time_info.playtime) + ": " + str(left_team_actions[e.time_info.playtime]))
        elif e.team_name == team_right_name:
            right_team_actions[e.time_info.playtime][e.player_number - 1] += 1
    # print(str(e.time_info.playtime) + ": " + str(right_team_actions[e.time_info.playtime]))
    # exit(0)

    # print(team_left_name)
    for i, c in enumerate(left_team_actions):
        if sum(c) < 20 and max(c) > 1:
            # print(str(i - 1) + ": " + str(left_team_actions[i - 1]) + " (" + str(left_team_actions[i]) + ")")
            holes[team_left_name].append(i - 1)
    # print(team_right_name)
    for i, c in enumerate(right_team_actions):
        if sum(c) < 20 and max(c) > 1:
            # print(str(i - 1) + ": " + str(right_team_actions[i - 1]) + " (" + str(right_team_actions[i]) + ")")
            holes[team_right_name].append(i - 1)

    return holes
