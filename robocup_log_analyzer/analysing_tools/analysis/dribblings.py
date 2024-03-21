from typing import List, Dict
from ..datamodel.datamodel import Kick, Dash


# TODO: Compare with loganalyzer3 results
def count_dribblings(kicks: List[Kick], dashes: List[Dash], team_left_name: str, team_right_name: str) \
        -> Dict[str, int]:
    """
    Counts the amount of dribblings of the game according to the teams

    :param kicks: a list of all kicks(including tackles?) in the game (ordered by playtime)
    :param dashes: a list of all dashes in the game (ordered by playtime)
    :param team_left_name: name of the left team
    :param team_right_name: name of the right team
    :return: a dict with the team names as keys and the amount of dribblings as values
    """
    dribblings_of_teams = {team_left_name: 0, team_right_name: 0}

    dash_iter = iter(dashes)
    dash = next(dash_iter)

    last_kick = kicks[0]
    for kick in kicks[1:]:
        # if the same player does to consecutive kicks
        if kick.player_number == last_kick.player_number and \
                kick.team_name == last_kick.team_name:
            # while dashes executed are between the kicks
            while dash.time_info.playtime < kick.time_info.playtime:
                # if the player that kicked did the dash
                if dash.player_number == last_kick.player_number and \
                        dash.team_name == last_kick.team_name:
                    dribblings_of_teams[last_kick.team_name] += 1

                try:
                    dash = next(dash)
                except StopIteration:
                    # if no more dashes exist, we are finished with counting
                    return dribblings_of_teams

        last_kick = kick

    # count the dribblings done after the last kick (not done ine the loop)
    done = False
    while not done:
        # if the player that kicked did the dash
        if dash.player_number == last_kick.player_number and \
                dash.team_name == last_kick.team_name:
            dribblings_of_teams[last_kick.team_name] += 1

        try:
            dash = next(dash)
        except StopIteration:
            done = True

    return dribblings_of_teams
