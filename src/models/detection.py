# ============================================================================
# src/models/detection.py
# 탐지 데이터 모델
# ============================================================================


from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class Detection:
    """객체 탐지 결과"""
    class_id: int
    class_name: str
    confidence: float
    bbox: np.ndarray  # [x1, y1, x2, y2]
    distance: float

    @property
    def center(self) -> Tuple[int, int]:
        """바운딩 박스 중심점"""
        x1, y1, x2, y2 = self.bbox
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))

    @property
    def width(self) -> int:
        """바운딩 박스 너비"""
        return int(self.bbox[2] - self.bbox[0])

    @property
    def height(self) -> int:
        """바운딩 박스 높이"""
        return int(self.bbox[3] - self.bbox[1])

    def is_dangerous(self, threshold: float = 5.0) -> bool:
        """위험 거리 판단"""
        return self.distance < threshold


@dataclass
class LaneLines:
    """차선 정보"""
    left_lane: Tuple[int, int, int, int] | None = None
    right_lane: Tuple[int, int, int, int] | None = None

    def is_complete(self) -> bool:
        """양쪽 차선 모두 감지되었는지"""
        return self.left_lane is not None and self.right_lane is not None

    def get_center_offset(self, frame_width: int) -> int:
        """차선 중심과 화면 중심의 오프셋"""
        if not self.is_complete():
            return 0

        lane_center = (self.left_lane[0] + self.right_lane[0]) // 2
        frame_center = frame_width // 2
        return frame_center - lane_center
