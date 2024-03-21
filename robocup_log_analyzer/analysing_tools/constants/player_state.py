from enum import Enum


class PlayerState(Enum):
    DISABLE =         0x00000000
    STAND =           0x00000001
    KICK =            0x00000002
    KICK_FAULT =      0x00000004
    GOALIE =          0x00000008
    CATCH =           0x00000010
    CATCH_FAULT =     0x00000020
    BALL_TO_PLAYER =  0x00000040
    PLAYER_TO_BALL =  0x00000080
    DISCARD =         0x00000100
    LOST =            0x00000200 # [I.Noda:00/05/13] added for 3D viewer/commentator/small league
    BALL_COLLIDE =    0x00000400 # player collided with the ball
    PLAYER_COLLIDE =  0x00000800 # player collided with another player
    TACKLE =          0x00001000
    TACKLE_FAULT =    0x00002000
    BACK_PASS =       0x00004000
    FREE_KICK_FAULT = 0x00008000
    POST_COLLIDE =    0x00010000 # player collided with goal posts
    FOUL_CHARGED =    0x00020000 # player is frozen by intentional tackle foul
    YELLOW_CARD =     0x00040000
    RED_CARD =        0x00080000
    ILLEGAL_DEFENSE = 0x00100000
