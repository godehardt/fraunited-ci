from typing import List
from ..datamodel.datamodel import Player


def get_player_by_number_and_team_side(players: List[Player], team_side: str, playernumber: int) -> Player:
    for player in players:
        if player.player_number == playernumber and player.team_side == team_side:
            return player


def get_player_by_number_and_team_name(players: List[Player], team_name: str, playernumber: int, *, team_left_name: str,
                                       team_right_name: str) -> Player:
    for player in players:
        player_team_name = team_left_name if player.team_side == 'l' else team_right_name
        if player.player_number == playernumber and player_team_name == team_name:
            return player
