from typing import List, Dict
from ..datamodel.datamodel import Kick, RefereeDecision
from ..datamodel.datamodel import Ball


# TODO: UNFINISHED
def goal_miss_analysis(kicks: List[Kick], balls: List[Ball], referee_decisions: List[RefereeDecision],
                       team_left_name: str, team_right_name: str) -> Dict[str, List[List[int]]]:
    """
    This function analyses why a goal shot missed. Possible reasons are: Missed, Keeper caught the ball

    :param kicks: a list of all successful (singular) kicks (including tackles) in the game (ordered by playtime)
    :param balls: a list of all ball objects in the game with index == playtime-1
    :param referee_decisions:
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team

    :return:
    """
    pass
