# ============================================================================
# src/models/stats.py
# 통계 데이터 모델
# ============================================================================

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DetectionStats:
    """탐지 통계"""
    total_objects: int = 0
    dangerous_objects: int = 0
    fps: float = 0.0
    processing_time: float = 0.0
    object_counts: Dict[str, int] = field(default_factory=dict)

    def reset(self) -> None:
        """통계 초기화"""
        self.total_objects = 0
        self.dangerous_objects = 0
        self.fps = 0.0
        self.processing_time = 0.0
        self.object_counts.clear()