from ..datamodel.datamodel import RefereeDecision
from typing import List, Dict


def get_referee_decision_as_playtime_dict(decisions: List[RefereeDecision]) -> Dict[int, List[RefereeDecision]]:
    """
    Transforms a list of referee decisions into a dict with playtime as key

    :param decisions: list of all referee decisions
    :return: a dict of all referee decisions as a list with playtime as key
    """
    decision_dict = {}

    for d in decisions:
        playtime = d.time_info.playtime
        if playtime in decision_dict:
            decision_dict[playtime].append(d)
        else:
            decision_dict[d.time_info.playtime] = [d]

    return decision_dict
