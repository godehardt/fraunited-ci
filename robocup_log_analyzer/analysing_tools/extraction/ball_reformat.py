from ..datamodel.datamodel import Ball, TimeInfo
from ..constants.robocup_constants import GAME_OVER_TIME
from typing import List, Tuple


def get_ball_list_ordered_by_time(balls: List[Ball]) -> Tuple[List[Ball], List[List[Ball]]]:
    """
    Transforms a list of all balls (ordered by playtime) into a list of balls grouped by timesteps and a list of balls
    only containing balls during playtime

    :param balls: a list of all ball objects in the game (ordered by playtime)
    :return: a list of balls ordered by playtime (pausetime balls excluded) and a list of balls ordered and grouped by playtime
    !!! AT PLAYTIME 3000 (index 2999) THE VALUE WILL ALWAYS BE NONE, BECAUSE THERE IS NO "SHOW 3000" IN THE RCG FILES !!!
    """
    balls_per_timestep = [[] for _ in range(GAME_OVER_TIME)]
    balls_during_playtime = [None for _ in range(GAME_OVER_TIME)]

    for ball in balls:
        playtime = ball.time_info.playtime -1

        pausetime = len(balls_per_timestep[playtime])
        if pausetime == 0:
            balls_per_timestep[playtime].append(ball)
            balls_during_playtime[playtime] = ball
        else:
            # create a ball with the new time_info
            time_info = TimeInfo(playtime, pausetime)
            # dataclasses.replace takes more than twice as long ?
            balls_per_timestep[playtime].append(Ball(x=ball.x, y=ball.y, x_velocity=ball.x_velocity,
                                                     y_velocity=ball.y_velocity, time_info=time_info))

    return balls_during_playtime, balls_per_timestep
