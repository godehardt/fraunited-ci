import math
from typing import List, Dict, Tuple
from ..constants.robocup_constants import MAX_STAMINA, HALF_TIME
from ..datamodel.datamodel import Player, Ball, Dash


#TODO: test
def stamina_low_percentage(players: List[List[Player]], team_left_name: str, team_right_name: str, *,
                           low_stamina_percentage: float = 0.1) -> Dict[str, Dict[int, List[int]]]:
    """
    This function calculates at what timesteps a players stamina dropped below a certain percentage

    :param players: A list that contains all players of a timestep for evey timestep with index == playtime-1
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :param low_stamina_percentage: the percentage at which stamina counts as low [0.0..1.0]

    :return: a dict with the team names as keys and the players as a Dict with key==player_number containing a list with
    all timesteps in which the stamina dropped below the given percentage
    """
    low_stamina_team_dict = {team_left_name: {i: [] for i in range(start=1, stop=12)},
                             team_right_name: {i: [] for i in range(start=1, stop=12)}}

    low_stamina = MAX_STAMINA * low_stamina_percentage

    for timestep, players_at_t in enumerate(players, start=1):
        for player in players_at_t:
            if player.stamina < low_stamina:
                if player.team_side == 'left':
                    team_name = team_left_name
                else:
                    team_name = team_right_name
                low_stamina_team_dict[team_name][player.player_number].append(timestep)

    return low_stamina_team_dict


#TODO: UNFINISHED
def dashes_away_from_ball(dashes: List[Dash], players: List[List[Player]], balls: List[Ball], team_left_name: str,
                          team_right_name: str, *, near_radius: float = 5.0) -> Dict[str, Dict[int, List[int]]]:
    """
    Calculates the timesteps of dashes that happened when a player was not near the ball for each player and team

    :param dashes: a list of all dashes (ordered by playtime)
    :param players: a list that contains all players of a timestep for evey timestep with index == playtime-1
    :param balls: a list of all ball objects in the game with index == playtime-1
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :param near_radius: the radius in meter which is considered near

    :return: a dict with the team names as keys and the players as a Dict with key==player_number containing a list with
    all timesteps in which a player dashed while away from the ball
    """
    dashes_team_dict = {team_left_name: {i: [] for i in range(start=1, stop=12)},
                        team_right_name: {i: [] for i in range(start=1, stop=12)}}


    for dash in dashes:
        players_at_t = players[dash.time_info.playtime]
        # TODO: Get player from players_at_t


# TODO: Correctness not tested
def get_stamina_usage_by_distance_per_player(players: List[List[Player]], balls: List[Ball], team_left_name: str,
                                             team_right_name: str, *,
                                             distance_classes: List[float] = None) -> \
        Dict[str, Dict[float, List[Tuple[float, float]]]]:
    """
    This function calculates the stamina usage of every player related to their distance to the ball.

    :param players: A list that contains all players of a timestep for evey timestep with index == playtime-1 (pausetime excluded)
    :param balls: a list of all ball objects in the game with index == playtime-1
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :param distance_classes: distances from the ball used for grouping the stamina usage (lower boundary).
    Zero is always the smallest distance class.

    :return: a dict with the team names as key, containing a dict with the distance classes as key, containing a list
    with index=playernumber-1 a tuple with the total and average stamina usage (per cycles in this distance) as value
    {team_name: {distance_class: [(total, average), ...]}}
    """
    distance_classes = distance_classes if distance_classes is not None else [5.0, 10.0, 15.0, 25.0, 50.0]
    # add zero as d_class
    distance_classes.append(0.0)
    distance_classes = sorted(distance_classes)
    stamina_usage_per_team = {team_left_name: {d_class: [[0, 0] for _ in range(11)] for d_class in distance_classes},
                              team_right_name: {d_class: [[0, 0] for _ in range(11)] for d_class in distance_classes}}

    last_step_stamina = [p.stamina for p in players[0]]
    last_step_capacity = [p.stamina_capacity for p in players[0]]
    for t, (ball_at_t, players_at_t) in enumerate(zip(balls, players)):
        if t == HALF_TIME-1:
            # reset the last step stamina because of regeneration
            last_step_stamina = [p.stamina for p in players[HALF_TIME]]  # no -1, because we need the next timestep
            last_step_capacity = [p.stamina_capacity for p in players[HALF_TIME]]  # no -1, because we need the next timestep
            # skip halftime, because there is no information for balls and players
            continue
        team_name = team_left_name
        for i, player in enumerate(players_at_t):
            if i == 11:
                team_name = team_right_name
            # calculate the distance between the ball and the player
            distance = math.hypot(ball_at_t.x - player.x, ball_at_t.y - player.y)
            # the distance class is the biggest class that is smaller than the distance
            d_class = list(filter(lambda dc: dc < distance, distance_classes))[-1]

            # calculated regenerated stamina
            regenerated_stamina = last_step_capacity[i] - player.stamina_capacity
            # calculate used stamina
            # BUG IN THE ROBOCUP SERVER: STAMINA CAPACITY GETS SEND AS A ROUNDED INT AND DOES NOT DEPICT REALITY. ERROR < 1.0
            used_stamina = max(0.0, last_step_stamina[i] + regenerated_stamina - player.stamina)
            # store used stamina to total stamina
            stamina_usage_per_team[team_name][d_class][player.player_number-1][0] += used_stamina
            last_step_stamina[i] = player.stamina
            last_step_capacity[i] = player.stamina_capacity
            # store number of entries in distance class for later calculation
            stamina_usage_per_team[team_name][d_class][player.player_number-1][1] += 1

    # calculate average stamina for every distance class and player
    for team_name, d_classes in stamina_usage_per_team.items():
        for d_class, players in d_classes.items():
            for i, player_stamina in enumerate(players):
                total_stamina = player_stamina[0]
                n_entries = player_stamina[1]

                # calculate the average stamina usage
                if n_entries > 0:
                    average_stamina = total_stamina / n_entries
                else:
                    average_stamina = 0.0
                # make the stamina entry a tuple
                stamina_usage_per_team[team_name][d_class][i] = (total_stamina, average_stamina)

    return stamina_usage_per_team


def get_players_near_ball(players: List[Player], ball: Ball, *, near_radius: float = 5.0) -> List[Player]:
    """
    Calculates what players are near the ball and returns them in a list

    :param players: a list of all players in a timestep
    :param ball: the ball at the same timestep as the players
    :param near_radius: the radius in meter which is considered near

    :return: a list of all players near the ball
    """
    players_near_ball = []

    for player in players:
        if is_inside_circle(player.x, player.y, ball.x, ball.y, near_radius):
            players_near_ball.append(player)

    return players_near_ball


def get_players_away_from_ball(players: List[Player], ball: Ball, *, near_radius: float = 5.0) -> List[Player]:
    """
    Calculates what players are away from the ball and returns them in a list

    :param players: a list of all players in a timestep
    :param ball: the ball at the same timestep as the players
    :param near_radius: the radius in meter which is considered near

    :return: a list of all players away from the ball
    """
    players_away_from_ball = []

    for player in players:
        if not is_inside_circle(player.x, player.y, ball.x, ball.y, near_radius):
            players_away_from_ball.append(player)

    return players_away_from_ball


def is_inside_circle(x: float, y: float, center_x: float, center_y: float, radius: float) -> bool:
    dx = abs(x - center_x)
    dy = abs(y - center_y)

    ## optimizations
    # check if x is outside the circle
    if dx > radius:
        return False
    # check if y is outside the circle
    elif dy > radius:
        return False
    # check if point is inside diamond within the circle
    elif dx + dy <= radius:
        return True
    ## optimization end
    else:
        # check if point is within circle with pythagoras (dx²+dy²<=radius²)
        return (dx * dx) + (dy * dy) <= (radius * radius)



