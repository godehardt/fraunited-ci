from typing import List, Tuple
from ..constants.robocup_constants import GAME_OVER_TIME
from ..constants.player_state import PlayerState
from ..datamodel.datamodel import Kick, Tackle, TimeInfo, Player
from ..extraction import helper_functions as helper_funcs


def get_successful_kicks_tackles(kicks: List[Kick], tackles: List[Tackle], players: List[List[Player]],
                                 team_left_name: str, team_right_name: str) -> Tuple[List[Kick], List[List[Kick]]]:
    """
    This functions returns all kicks and tackles that are successful. It also transforms the tackles into kicks, since
    they are a special type of kick.

    :param kicks: a list of all kicks in the game (ordered by playtime)
    :param tackles: a list of all tackles in the game (ordered by playtime)
    :param players: a list that contains a list with every player for a timestep with playtime-1 == index
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team

    :return a list of all successful kicks and tackles (as kick) (ordered by playtime) and the same list but with
        simultaneous actions in the same sublist
    """
    real_kicks = []
    real_kicks_as_lists = []

    kick_iter = iter(kicks)
    tackle_iter = iter(tackles)
    kicks_done = False
    tackles_done = False
    # set initial kick
    try:
        kick = next(kick_iter)
    except StopIteration:
        kick = Kick(team_name="", player_number=-1, power=None, direction=None, time_info=TimeInfo(GAME_OVER_TIME+1, 0))
        kicks_done = True
    # set initial tackle
    try:
        tackle = next(tackle_iter)
    except StopIteration:
        tackle = Tackle(team_name="", player_number=-1, power_or_direction=None, foul=None, time_info=TimeInfo(GAME_OVER_TIME+1, 0))
        tackles_done = True

    while not (kicks_done and tackles_done):
        if tackles_done or (not kicks_done and kick.time_info.playtime <= tackle.time_info.playtime):
            # check if the kick was successful by checking if the playerstate at kicktime contains a failed kick
            # playtime and not playtime -1, because we need the state of the next timestep
            player = helper_funcs.get_player_by_number_and_team_name(players[kick.time_info.playtime], kick.team_name,
                                                                     kick.player_number, team_left_name=team_left_name,
                                                                     team_right_name=team_right_name)
            # player can be None the kick happened in the last cycle of a half time
            if player is not None and \
                    not (int(player.state, 16) & int(PlayerState.KICK_FAULT.value) == PlayerState.KICK_FAULT.value):
                if real_kicks_as_lists and real_kicks_as_lists[-1][0].time_info.playtime == kick.time_info.playtime:
                    real_kicks_as_lists[-1].append(kick)
                else:
                    real_kicks_as_lists.append([kick])
                real_kicks.append(kick)

            # set next kick
            try:
                kick = next(kick_iter)
            except StopIteration:
                kicks_done = True
        elif kicks_done or (not tackles_done and tackle.time_info.playtime <= kick.time_info.playtime):
            # check if the kick was successful by checking if the playerstate at tackletime contains a failed tackle
            # playtime and not playtime -1, because we need the state of the next timestep
            player = helper_funcs.get_player_by_number_and_team_name(players[tackle.time_info.playtime],
                                                                     tackle.team_name, tackle.player_number,
                                                                     team_left_name=team_left_name,
                                                                     team_right_name=team_right_name)
            # player can be None the kick happened in the last cycle of a half time
            if player is not None and \
                    not (int(player.state, 16) & int(PlayerState.TACKLE_FAULT.value) == PlayerState.TACKLE_FAULT.value):
                tackle_kick = Kick(team_name=tackle.team_name, player_number=tackle.player_number, power=tackle.power_or_direction,
                                   direction=tackle.power_or_direction, time_info=tackle.time_info)
                if real_kicks_as_lists and real_kicks_as_lists[-1][0].time_info.playtime == tackle.time_info.playtime:
                    real_kicks_as_lists[-1].append(tackle_kick)
                else:
                    real_kicks_as_lists.append([tackle_kick])
                real_kicks.append(tackle_kick)

            # set next tackle
            try:
                tackle = next(tackle_iter)
            except StopIteration:
                tackles_done = True

    return real_kicks, real_kicks_as_lists


def get_successful_kicks(kicks: List[Kick], players: List[List[Player]], team_left_name: str, team_right_name: str) \
        -> List[Kick]:
    """
    This function returns all successful kicks from a list

    :param kicks: a list of all kicks in the game (ordered by playtime)
    :param players: a list that contains a list with every player for a timestep with playtime-1 == index
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :return: a list of successful kicks (ordered by playtime)
    """
    successful_kicks = []

    for kick in kicks:
        # playtime and not playtime -1, because we need the state of the next timestep
        player = helper_funcs.get_player_by_number_and_team_name(players[kick.time_info.playtime], kick.team_name,
                                                                 kick.player_number, team_left_name=team_left_name,
                                                                 team_right_name=team_right_name)
        # player can be None the kick happened in the last cycle of a half time
        if player is not None and \
                not (int(player.state, 16) & int(PlayerState.KICK_FAULT.value) == PlayerState.KICK_FAULT.value):
            successful_kicks.append(kick)

    return successful_kicks


def get_successful_tackles(tackles: List[Tackle], players: List[List[Player]], team_left_name: str,
                           team_right_name: str) -> List[Tackle]:
    """
    This function returns all successful tackles from a list

    :param tackles: a list of all tackles in the game (ordered by playtime)
    :param players: a list that contains a list with every player for a timestep with playtime-1 == index
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :return: a list of successful tackles (ordered by playtime)
    """
    successful_tackles = []

    for tackle in tackles:
        # playtime and not playtime -1, because we need the state of the next timestep
        player = helper_funcs.get_player_by_number_and_team_name(players[tackle.time_info.playtime], tackle.team_name,
                                                                 tackle.player_number, team_left_name=team_left_name,
                                                                 team_right_name=team_right_name)
        # player can be None the tackle happened in the last cycle of a half time
        if player is not None and \
                not (int(player.state, 16) & int(PlayerState.TACKLE_FAULT.value) == PlayerState.TACKLE_FAULT.value):
            successful_tackles.append(tackle)

    return successful_tackles


def get_singular_kicks(kicks: List[Kick]) -> List[Kick]:
    """
    This functions filters kicks from a list that where executed at the same time

    :param kicks: a list of all kicks (ordered by playtime)
    :return: a list of all kicks that are the only kick executed in a timestep (ordered by playtime)
    """

    singular_kicks = []
    last_kick = kicks[0]
    new_timestep = True
    for kick in kicks[1:]:
        if kick.time_info.playtime == last_kick.time_info.playtime:
            new_timestep = False
        elif kick.time_info.playtime != last_kick.time_info.playtime and \
                new_timestep:
            singular_kicks.append(last_kick)
        else:
            new_timestep = True

        last_kick = kick

    # append last kick if it was singular
    if new_timestep:
        singular_kicks.append(kicks[-1])

    return singular_kicks


def get_singular_tackles(tackles: List[Tackle]) -> List[Tackle]:
    """
    This functions filters tackles from a list that where executed at the same time

    :param tackles: a list of all tackles (ordered by playtime)
    :return: a list of all tackles that are the only tackle executed in a timestep (ordered by playtime)
    """

    singular_tackles = []
    last_tackle = tackles[0]
    new_timestep = True
    for tackle in tackles[1:]:
        if tackle.time_info.playtime == last_tackle.time_info.playtime:
            new_timestep = False
        elif tackle.time_info.playtime != last_tackle.time_info.playtime and \
                new_timestep:
            singular_tackles.append(last_tackle)
        else:
            new_timestep = True

        last_tackle = tackle

    # append last kick if it was singular
    if new_timestep:
        singular_tackles.append(tackles[-1])

    return singular_tackles
