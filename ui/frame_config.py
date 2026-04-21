"""Configuration object for the main Tkinter frame."""

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple


MoveSequence = Tuple[str, ...]
ScrambleGroups = Sequence[Sequence[MoveSequence]]


@dataclass
class FrameConfig:
    cube_size: int = 3
    F2L: bool = False
    OLL: bool = False
    Centers: bool = False
    Edges: bool = False
    Cross: bool = False

    ai_search_modes: Optional[Sequence[str]] = None
    initial_scramble_groups: Optional[ScrambleGroups] = None

    lrs: Optional[Sequence[float]] = None
    wdlrs: Optional[Sequence[float]] = None
    skip_search: Optional[Sequence[bool]] = None
    weight_decay: Optional[Sequence[bool]] = None
    adam: Optional[Sequence[bool]] = None
    lr_vs: Optional[Sequence[float]] = None
    lr_hs: Optional[Sequence[float]] = None
    out_cs: Optional[Sequence[float]] = None
    search3_cs: Optional[Sequence[float]] = None

    transform_idx: Optional[Sequence[int]] = None
    flip_inside_idx: Optional[Sequence[bool]] = None
    priority_list: Optional[Sequence[Sequence[str]]] = None
    bootstrap_datas: Optional[Sequence[MoveSequence]] = None
