from typing import List, Tuple
from ..datamodel.datamodel import Player, TimeInfo
from ..constants.robocup_constants import GAME_OVER_TIME


def get_player_list_ordered_by_time(players: List[Player]) -> Tuple[List[List[Player]], List[List[Player]]]:
    """
    Transforms a list of all players (ordered by playtime) into a list of players for every timestep

    :param players: a list of all player objects in the game (ordered by playtime)
    :return: a list that contains all player objects of a timestep for evey timestep with index == playtime-1
    (pausetime excluded) and a list that contains all player objects of a timestep for evey timestep with
    index == playtime-1 (pausetime included)
    """
    players_per_timestep = [[] for _ in range(GAME_OVER_TIME)]
    players_per_timestep_playtime_only = [[] for _ in range(GAME_OVER_TIME)]

    for player in players:
        # set the new playtime
        playtime = player.time_info.playtime

        # TODO: Handle red cards (less players)
        # calculate the pausetime
        pausetime = len(players_per_timestep[playtime -1]) // 22   # if moves happened during pause time (22 count of all players

        if pausetime == 0:
            players_per_timestep[playtime - 1].append(player)
            players_per_timestep_playtime_only[playtime - 1].append(player)
        else:
            # create a player with the new time_info
            time_info = TimeInfo(playtime, pausetime)
            # dataclasses.replace takes more than twice as long
            players_per_timestep[playtime - 1].append(Player(team_side=player.team_side,
                                                             player_number=player.player_number, type=player.type,
                                                             state=player.state, x=player.x, y=player.y,
                                                             x_velocity=player.x_velocity, y_velocity=player.y_velocity,
                                                             body_angle=player.body_angle, neck_angle=player.neck_angle,
                                                             point_to_x=player.point_to_x, point_to_y=player.point_to_y,
                                                             view_quality=player.view_quality,
                                                             view_area=player.view_area, stamina=player.stamina,
                                                             stamina_effort=player.stamina_effort,
                                                             stamina_recovery=player.stamina_recovery,
                                                             stamina_capacity=player.stamina_capacity,
                                                             time_info=time_info))
    return players_per_timestep_playtime_only, players_per_timestep


def get_player_list_ordered_by_time_fast(players: List[Player]) -> List[List[Player]]:
    """
    Transforms a list of all players (ordered by playtime) into a list of players for every timestep

    :param players: a list of all player objects in the game (ordered by playtime)
    :return: a list that contains all player objects of a timestep for evey timestep with index == playtime-1
    """
    players_per_timestep = [[] for _ in range(GAME_OVER_TIME)]

    player_counter = 0
    pausetime = 0
    last_playtime = 1
    for player in players:
        # set the new playtime
        playtime = player.time_info.playtime
        player_counter += 1

        # TODO: Handle red cards (less players)
        if player_counter > 22:
            if last_playtime != playtime:
                player_counter = 1
                pausetime = 0
                last_playtime = playtime
            elif last_playtime == playtime and player_counter % 22 == 1:
                pausetime += 1

        if pausetime == 0:
            players_per_timestep[playtime - 1].append(player)
        else:
            # create a player with the new time_info
            time_info = TimeInfo(playtime, pausetime)
            # dataclasses.replace takes more than twice as long
            players_per_timestep[playtime - 1].append(Player(team_side=player.team_side,
                                                             player_number=player.player_number, type=player.type,
                                                             state=player.state, x=player.x, y=player.y,
                                                             x_velocity=player.x_velocity, y_velocity=player.y_velocity,
                                                             body_angle=player.body_angle, neck_angle=player.neck_angle,
                                                             point_to_x=player.point_to_x, point_to_y=player.point_to_y,
                                                             view_quality=player.view_quality,
                                                             view_area=player.view_area, stamina=player.stamina,
                                                             stamina_effort=player.stamina_effort,
                                                             stamina_recovery=player.stamina_recovery,
                                                             stamina_capacity=player.stamina_capacity,
                                                             focus_target=player.focus_target, time_info=time_info))
    return players_per_timestep
