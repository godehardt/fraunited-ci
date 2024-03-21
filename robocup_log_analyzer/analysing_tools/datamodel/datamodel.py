from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict, Any

from collections import defaultdict
from ..constants.referee_decisions import EnumRefereeDecision, EnumTeamSide

# Some definitions of the messages are here:
# https://github.com/rcsoccersim/rcssserver/blob/1b5076d0e7fd24f4c168d00446be94d66807b139/src/pcombuilder.h


##############
# Game State #
##############

@dataclass
class TimeInfo:
    playtime: int
    pausetime: int


@dataclass
class Ball:
    x: float
    y: float
    x_velocity: float
    y_velocity: float
    time_info: TimeInfo


@dataclass
class Player:
    team_side: str
    player_number: int
    type: int  # log3: hetero -> playertype?
    state: str  # hexadecimal
    x: float
    y: float
    x_velocity: float
    y_velocity: float
    body_angle: float
    neck_angle: float
    point_to_x: Optional[float]  # can be None
    point_to_y: Optional[float]  # can be None
    view_quality: str  # TODO: maybe change to enum
    view_area: int
    stamina: float
    stamina_effort: float
    stamina_recovery: float
    stamina_capacity: float
    # focus_target: int
    time_info: TimeInfo


##########
# Events #
##########

@dataclass
class RefereeDecision:
    decision: EnumRefereeDecision
    team_side: EnumTeamSide
    player_number_or_goals: Optional[int]
    time_info: TimeInfo


@dataclass
class Kick:
    team_name: str
    player_number: int
    power: float
    direction: float
    time_info: TimeInfo


@dataclass
class Tackle:
    team_name: str
    player_number: int
    power_or_direction: float
    foul: bool
    time_info: TimeInfo


@dataclass
class Dash:
    team_name: str
    player_number: int
    power: float
    direction: Optional[float]
    time_info: TimeInfo


@dataclass
class Turn:
    team_name: str
    player_number: int
    angle: float
    time_info: TimeInfo


@dataclass
class Goal:
    goals_l: int
    goals_r: int
    time_info: TimeInfo


@dataclass
class Playmode:
    mode: str
    time_info: TimeInfo


######################
# Static Information #
######################

@dataclass
class ServerParam:
    name: str
    value: Union[int, float, str]


@dataclass
class Message:
    parameter: int
    message: str
    time_info: TimeInfo


@dataclass(frozen=False)
class Game:
    team_l: Optional[str] = None
    team_r: Optional[str] = None
    balls: List[Ball] = field(default_factory=list)
    events: List[Union[Kick, Tackle, Dash, RefereeDecision]] = field(default_factory=list)
    players: List[Player] = field(default_factory=list)
    goals: List[Goal] = field(default_factory=list)
    playmode_changes: List[Playmode] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    referee_decisions: List[RefereeDecision] = field(default_factory=list)
    tackles: List[Tackle] = field(default_factory=list)
    dashes: List[Dash] = field(default_factory=list)
    turns: List[Turn] = field(default_factory=list)
    kicks: List[Kick] = field(default_factory=list)
    other_events: Dict[str, List[Any]] = field(default_factory=lambda: defaultdict(list))
    server_params: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    player_params: Dict[str, Union[int, float, str]] = field(default_factory=dict)
    player_types: Dict[int, Dict[str, Union[int, float, str]]] = field(default_factory=dict)
