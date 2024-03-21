from enum import Enum, unique
from typing import List


@unique
class EnumRefereeDecision(Enum):
    FREE_KICK_L = 'free_kick_l'
    FREE_KICK_R = 'free_kick_r'
    FOUL_CHARGE_L = 'foul_charge_l'
    FOUL_CHARGE_R = 'foul_charge_r'
    OFFSIDE_L = 'offside_l'
    OFFSIDE_R = 'offside_r'
    CORNER_KICK_L = 'corner_kick_l'
    CORNER_KICK_R = 'corner_kick_r'
    GOAL_KICK_L = 'goal_kick_l'
    GOAL_KICK_R = 'goal_kick_r'
    YELLOW_CARD_L = 'yellow_card_l'
    YELLOW_CARD_R = 'yellow_card_r'
    RED_CARD_L = 'red_card_l'
    RED_CARD_R = 'red_card_r'
    BACK_PASS_L = 'back_pass_l'
    BACK_PASS_R = 'back_pass_r'
    INDIRECT_FREE_KICK_L = 'indirect_free_kick_l'
    INDIRECT_FREE_KICK_R = 'indirect_free_kick_r'
    KICK_OFF_L = 'kick_off_l'
    KICK_OFF_R = 'kick_off_r'
    KICK_IN_L = 'kick_in_l'
    KICK_IN_R = 'kick_in_r'
    GOALIE_CATCH_BALL_L = 'goalie_catch_ball_l'
    GOALIE_CATCH_BALL_R = 'goalie_catch_ball_r'
    GOAL_L = 'goal_l'
    GOAL_R = 'goal_r'
    PLAY_ON = 'play_on'
    HALF_TIME = 'half_time'
    BEFORE_KICK_OFF = 'before_kick_off'
    TIME_UP = 'time_up'
    TIME_OVER = 'time_over'

    @staticmethod
    def get_kick_decisions() -> List['EnumRefereeDecision']:
        return [EnumRefereeDecision.FREE_KICK_L,
                EnumRefereeDecision.FREE_KICK_R,
                EnumRefereeDecision.GOAL_KICK_L,
                EnumRefereeDecision.GOAL_KICK_R,
                EnumRefereeDecision.CORNER_KICK_L,
                EnumRefereeDecision.CORNER_KICK_R,
                EnumRefereeDecision.INDIRECT_FREE_KICK_L,
                EnumRefereeDecision.INDIRECT_FREE_KICK_R,
                EnumRefereeDecision.KICK_OFF_L,
                EnumRefereeDecision.KICK_OFF_R,
                EnumRefereeDecision.GOALIE_CATCH_BALL_L,
                EnumRefereeDecision.GOALIE_CATCH_BALL_R,
                EnumRefereeDecision.OFFSIDE_L,
                EnumRefereeDecision.OFFSIDE_R,
                EnumRefereeDecision.KICK_IN_L,
                EnumRefereeDecision.KICK_IN_R]

    @staticmethod
    def get_sideless_decisions() -> List['EnumRefereeDecision']:
        return [EnumRefereeDecision.PLAY_ON,
                EnumRefereeDecision.HALF_TIME,
                EnumRefereeDecision.BEFORE_KICK_OFF,
                EnumRefereeDecision.TIME_UP,
                EnumRefereeDecision.TIME_OVER]


@unique
class EnumTeamSide(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NO_SIDE = 'no_side'
