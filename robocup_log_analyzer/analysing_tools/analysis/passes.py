import math
from collections import defaultdict
from typing import Dict, List
from ..datamodel.datamodel import Kick, Tackle, RefereeDecision, Ball
from ..datamodel.calculated_classes import Offside
from ..constants.referee_decisions import EnumRefereeDecision
from ..constants.robocup_constants import HALF_TIME


# differences to loganalyzer3 are because loganalyzer3 takes the timestep after a kick to calculate the last kick
def count_passes(kicks: List[List[Kick]], balls: List[Ball], ref_decisions: Dict[int, List[RefereeDecision]],
                 team_left_name: str, team_right_name: str) -> Dict[str, Dict[str, int]]:
    """
    This function counts all passes in the game according to their team and direction

    :param kicks: a list of all successful kicks (and tackles) of the game (ordered in sublists of playtime)
    :param balls: a list of all ball objects in the game with index == playtime-1
    :param ref_decisions: a dict of all referee decisions as a list with playtime as key
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :return: a dict with the team names as keys and as values a dict with the pass directions as keys and the amount as values
    """
    pass_routes_of_teams = {team_left_name: {'left': 0, 'right': 0, 'front': 0, 'back': 0},
                            team_right_name: {'left': 0, 'right': 0, 'front': 0, 'back': 0}}

    last_kick = kicks[0][0]
    neutral = False
    for kick in kicks[1:]:
        was_neutral = neutral
        neutral = len(kick) > 1
        current_playtime = kick[0].time_info.playtime

        # if the last kick happened before the half time break
        if last_kick.time_info.playtime < HALF_TIME <= current_playtime:
            # treat the last kick as being neutral
            was_neutral = True
            # if the current kick is exactly at HALF_TIME the kick does not count (there is no ball info for this timestep)
            if current_playtime == HALF_TIME:
                neutral = True
        # check if the pass was offside
        elif ref_decisions.get(current_playtime, False):
            for d in ref_decisions[current_playtime]:
                if d.decision == EnumRefereeDecision.OFFSIDE_L or \
                        d.decision == EnumRefereeDecision.OFFSIDE_R:
                    neutral = True

        # if the ball is still controlled by the same team but not the same player (a pass was played)
        if not neutral and not was_neutral and last_kick.team_name == kick[0].team_name and \
                last_kick.player_number != kick[0].player_number:
            # get the ball at the time of kick
            ball_last_kick = balls[last_kick.time_info.playtime - 1]  # drop the -1 for full loganalyzer3 behaviour
            # get the ball at the time of receiving it
            ball_current_kick = balls[current_playtime - 1]
            # set team_side
            team_side = 'l' if kick[0].team_name == team_left_name else 'r'
            # calculate pass direction
            if ball_last_kick is not None and ball_current_kick is not None:
                direction = get_pass_direction(ball_last_kick, ball_current_kick, team_side)

                pass_routes_of_teams[kick[0].team_name][direction] += 1

        if not neutral:
            last_kick = kick[0]

    return pass_routes_of_teams


# TODO: Compare with loganalyzer3 results
def count_through_passes(kicks: List[Kick], balls: List[Ball], offsides: List[Offside],
                         team_left_name: str, team_right_name: str) -> Dict[str, int]:
    pass_through_per_team = {team_left_name: 0,
                             team_right_name: 0}

    last_kick = kicks[0]
    for kick in kicks[1:]:
        # if the ball is still controlled by the same team but not the same player (a pass was played)
        if last_kick.team_name == kick.team_name and \
                last_kick.player_number != kick.player_number:
            # get the ball at the time of kick
            ball_last_kick = balls[last_kick.time_info.playtime - 1]
            # get the ball at the time of receiving it
            ball_current_kick = balls[kick.time_info.playtime - 1]

            # get offside for the correct time step
            offside = offsides[kick.time_info.playtime - 1]
            if kick.team_name == team_left_name:
                is_through_pass = check_through_pass(ball_last_kick, ball_current_kick, offside, 'l')
            else:
                is_through_pass = check_through_pass(ball_last_kick, ball_current_kick, offside, 'r')

            if is_through_pass:
                pass_through_per_team[kick.team_name] += 1

    return pass_through_per_team


def get_pass_direction(ball_at_kick: Ball, ball_at_receive: Ball, team_side: str) -> str:
    """
    This function calculates in what direction a pass went

    :param ball_at_kick: the ball at the time the pass started
    :param ball_at_receive: the ball at the time the pass was received
    :param team_side: the team side of the player that did the pass
    :return: 'front', 'left', 'right' or 'back'
    """
    # calculate the radian
    radian = math.atan2(ball_at_receive.y - ball_at_kick.y, ball_at_receive.x - ball_at_kick.x)
    # transform radian to degree
    degree = radian * 180 / math.pi

    if -45.0 < degree <= 45.0:
        return 'front' if team_side == 'l' else 'back'
    elif 45.0 < degree <= 135.0:
        return 'right' if team_side == 'l' else 'left'
    elif -135.0 < degree <= -45.0:
        return 'left' if team_side == 'l' else 'right'
    elif degree > 135.0 or degree <= -135.0:
        return 'back' if team_side == 'l' else 'front'


def check_through_pass(ball_at_kick: Ball, ball_at_receive: Ball, offside: Offside, team_side: str) -> bool:
    if team_side == 'l' \
            and ball_at_receive.x - ball_at_kick.x > 5.0 \
            and ball_at_receive.x > 15.0 \
            and offside.right_side < ball_at_receive.x:
        return True
    elif team_side == 'l' \
            and ball_at_receive.x - ball_at_kick.x < -5.0 \
            and ball_at_receive.x < -15.0 \
            and offside.left_side > ball_at_receive.x:
        return True

    return False


def pass_chain(kicks: List[Kick], tackles: List[Tackle], team_left_name: str, team_right_name: str, *,
               max_time_between_passes: int = 10) -> Dict[str, Dict[int, int]]:
    """
    This function returns all pass chains according to their length and team

    :param kicks: a list of all successful (singular) kicks in the game (ordered by playtime)
    :param tackles: a list of all successful (singular) tackles in the game (ordered by playtime)
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :param max_time_between_passes: the maximum amount of playtime that is allowed between two passes to be considered a chain
    :return: a dict with the team names as keys and as values a dict with the pass chain length as keys and the amount as values
    """
    # initialize dict with default value 0
    pass_chain_counters = {team_left_name: defaultdict(int),
                           team_right_name: defaultdict(int)}

    kick_iter = iter(kicks)
    tackle_iter = iter(tackles)

    kick = next(kick_iter)
    kicks_done = False
    # initialize first tackle
    if len(tackles) == 0:
        tackles_done = True
    else:
        tackles_done = False
        tackle = next(tackle_iter)
    last_player_team = ""
    last_player_number = -1
    last_action_time = -max_time_between_passes - 1
    current_pass_chain_length = 0
    while not kicks_done:
        # if a tackle is the next action
        if not tackles_done and tackle.time_info.playtime < kick.time_info.playtime:
            # a tackle always interrupts a pass chain
            # if there was an actual pass chain
            if current_pass_chain_length > 1:
                # count the pass chain
                pass_chain_counters[last_player_team][current_pass_chain_length] += 1

            # start a new pass chain with this tackle
            current_pass_chain_length = 1
            # # save information about this pass
            last_player_team = tackle.team_name
            last_player_number = tackle.player_number
            last_action_time = tackle.time_info.playtime

            # set tackle to the next tackle in the list
            try:
                tackle = next(tackle_iter)
            except StopIteration:
                tackles_done = True
        # if a kick is the next action
        elif tackles_done or kick.time_info.playtime < tackle.time_info.playtime:
            # if the pass chain continues
            if last_player_team == kick.team_name and last_player_number != kick.player_number \
                    and kick.time_info.playtime - last_action_time <= max_time_between_passes:
                # the pass chain continues
                current_pass_chain_length += 1
            # if a pass chain existed, but it doesn't continue
            elif current_pass_chain_length > 1:
                # count the pass chain
                pass_chain_counters[last_player_team][current_pass_chain_length] += 1
                # start a new pass chain with this kick
                current_pass_chain_length = 1
            # if no pass chain existed
            else:
                # start a new pass chain with this kick
                current_pass_chain_length = 1

            # save information about this pass
            last_player_team = kick.team_name
            last_player_number = kick.player_number
            last_action_time = kick.time_info.playtime

            # set kick to the next kick in the list
            try:
                kick = next(kick_iter)
            except StopIteration:
                kicks_done = True
        # if tackle and kick happen at the same time
        elif tackle.time_info.playtime == kick.time_info.playtime:
            # save the pass chain if it exists
            if current_pass_chain_length > 1:
                # count the pass chain
                pass_chain_counters[last_player_team][current_pass_chain_length] += 1
            # dont count the pass
            current_pass_chain_length = 0
            # reset the last kick memory
            last_player_team = ""
            last_player_number = -1
            last_action_time = -max_time_between_passes - 1
            # set kick to the next kick in the list
            try:
                kick = next(kick_iter)
            except StopIteration:
                kicks_done = True
            # set tackle to the next tackle in the list
            try:
                tackle = next(tackle_iter)
            except StopIteration:
                tackles_done = True

    # add the last pass chain of the game
    if current_pass_chain_length > 1:
        pass_chain_counters[last_player_team][current_pass_chain_length] += 1

    # transform default dict to dict
    pass_chain_counters[team_left_name] = dict(pass_chain_counters[team_left_name])
    pass_chain_counters[team_right_name] = dict(pass_chain_counters[team_right_name])

    return pass_chain_counters
