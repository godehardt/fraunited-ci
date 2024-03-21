from dataclasses import dataclass
from ..datamodel.datamodel import TimeInfo
from typing import Dict


@dataclass(frozen=True)
class Offside:
    right_side: int
    left_side: int
    time_info: TimeInfo


@dataclass
class Analysis:
    pass_counts: Dict[str, int]
    through_pass_count: int
    pass_chain_length_counts: Dict[int, int]

