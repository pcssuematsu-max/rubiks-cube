"""Configuration object for the main Tkinter frame."""

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple


MoveSequence = Tuple[str, ...]
ScrambleGroups = Sequence[Sequence[MoveSequence]]


@dataclass
class FrameConfig:
    """Frame 起動時に渡す実験設定をまとめた dataclass。"""

    # Cube mode selection.
    puzzle_type: str = 'rubiks'
    cube_size: int = 3
    F2L: bool = False
    OLL: bool = False
    Centers: bool = False
    Edges: bool = False
    Cross: bool = False

    # Search / scramble initialization.
    ai_search_modes: Optional[Sequence[str]] = None
    initial_scramble_groups: Optional[ScrambleGroups] = None
    transform_random: bool = False
    search3_progress: Optional[Sequence[bool]] = None

    # Optimizer / learning toggles.
    lrs: Optional[Sequence[float]] = None
    wdlrs: Optional[Sequence[float]] = None
    skip_search: Optional[Sequence[bool]] = None
    weight_decay: Optional[Sequence[bool]] = None
    adam: Optional[Sequence[bool]] = None

    # Additional runtime coefficients for each AI.
    lr_vs: Optional[Sequence[float]] = None
    lr_hs: Optional[Sequence[float]] = None
    out_cs: Optional[Sequence[float]] = None
    search3_cs: Optional[Sequence[float]] = None
    pv_ratios: Optional[Sequence[float]] = None

    # Solve-time transform / priority settings.
    transform_idx: Optional[Sequence[int]] = None
    flip_inside_idx: Optional[Sequence[bool]] = None
    priority_list: Optional[Sequence[Sequence[str]]] = None

    # Extra bootstrap training data appended at startup.
    bootstrap_datas: Optional[Sequence[MoveSequence]] = None

    def __post_init__(self):
        """AI 数に依存する設定長の整合性を確認する。"""
        ai_count = self._ai_count()
        self._validate_ai_sequence_length('lrs', self.lrs, ai_count)
        self._validate_ai_sequence_length('wdlrs', self.wdlrs, ai_count)
        self._validate_ai_sequence_length('skip_search', self.skip_search, ai_count)
        self._validate_ai_sequence_length('weight_decay', self.weight_decay, ai_count)
        self._validate_ai_sequence_length('adam', self.adam, ai_count)
        self._validate_ai_sequence_length('lr_vs', self.lr_vs, ai_count)
        self._validate_ai_sequence_length('lr_hs', self.lr_hs, ai_count)
        self._validate_ai_sequence_length('out_cs', self.out_cs, ai_count)
        self._validate_ai_sequence_length('search3_cs', self.search3_cs, ai_count)
        self._validate_ai_sequence_length('pv_ratios', self.pv_ratios, ai_count)
        self._validate_ai_sequence_length('transform_idx', self.transform_idx, ai_count)
        self._validate_ai_sequence_length('flip_inside_idx', self.flip_inside_idx, ai_count)
        self._validate_ai_sequence_length('priority_list', self.priority_list, ai_count)
        self._validate_ai_sequence_length('search3_progress', self.search3_progress, ai_count)
        self._validate_initial_scramble_groups()

    def _ai_count(self):
        """設定から想定される AI 数を返す。"""
        if self.ai_search_modes is None:
            return 20
        return len(self.ai_search_modes)

    def _validate_ai_sequence_length(self, field_name, values, ai_count):
        """AI ごとの設定列長が AI 数と一致するか確認する。"""
        if values is None:
            return
        if len(values) != ai_count:
            raise ValueError(
                f"FrameConfig.{field_name} must have length {ai_count}, got {len(values)}."
            )

    def _validate_initial_scramble_groups(self):
        """初期 scramble 群が stage 数に対応する形か確認する。"""
        if self.initial_scramble_groups is None:
            return
        if len(self.initial_scramble_groups) != 8:
            raise ValueError(
                "FrameConfig.initial_scramble_groups must have length 8."
            )
