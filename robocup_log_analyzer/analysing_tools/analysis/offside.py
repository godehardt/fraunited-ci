from typing import List
from ..datamodel.datamodel import Player, TimeInfo
from ..constants.player_state import PlayerState
from ..datamodel.calculated_classes import Offside
from ..constants.robocup_constants import GAME_OVER_TIME


def calc_offside_x(players: List[List[Player]]) -> List[Offside]:
    """
    Calculates for every timestep the offside line for both teams

    :param players: a list that contains a list of player or every timestep with index == playtime-1
    :return: a list of offside objects with index == playtime-1
    """
    offsides = []
    for playtime in range(1, GAME_OVER_TIME+1):
        # off_l = min([player.x
        #             for player in players[playtime-1]
        #             if player.x < 0.0
        #             and player.team_side == 'l'
        #             and (int(player.state, 16) & int(PlayerState.GOALIE.value)) != PlayerState.GOALIE.value],
        #             default=0.0)
        # off_r = max([player.x
        #             for player in players[playtime-1]
        #             if player.x > 0.0
        #             and player.team_side == 'r'
        #             and (int(player.state, 16) & int(PlayerState.GOALIE.value)) != PlayerState.GOALIE.value],
        #             default=0.0)

        # 0.0, because offside is only on the enemy side
        off_l = 0.0
        off_r = 0.0
        for player in players[playtime-1]:
            if player.team_side == 'l' \
                    and (int(player.state, 16) & int(PlayerState.GOALIE.value)) != PlayerState.GOALIE.value:
                off_l = min(off_l, player.x)
            elif player.team_side == 'r' \
                    and (int(player.state, 16) & int(PlayerState.GOALIE.value)) != PlayerState.GOALIE.value:
                off_r = max(off_r, player.x)

        offsides.append(Offside(left_side=off_l, right_side=off_r, time_info=TimeInfo(playtime, 0)))

    return offsides
