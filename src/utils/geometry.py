# ============================================================================
# src/utils/geometry.py
# 기하학 연산 유틸리티
# ============================================================================


import numpy as np
import cv2
from typing import Tuple, List


class GeometryUtils:
    """기하학 연산 유틸리티"""

    @staticmethod
    def estimate_distance(bbox_width: float,
                          focal_length: float = 800.0,
                          known_width: float = 1.8) -> float:
        """거리 추정"""
        if bbox_width == 0:
            return float('inf')
        return (known_width * focal_length) / bbox_width

    @staticmethod
    def create_roi_vertices(width: int, height: int,
                            top_ratio: float = 0.6,
                            left_ratio: float = 0.1,
                            right_ratio: float = 0.9) -> np.ndarray:
        """ROI 영역 정점 생성"""
        return np.array([[
            (int(width * left_ratio), height),
            (int(width * 0.4), int(height * top_ratio)),
            (int(width * 0.6), int(height * top_ratio)),
            (int(width * right_ratio), height)
        ]], dtype=np.int32)

    @staticmethod
    def create_roi_mask(shape: Tuple[int, ...], vertices: np.ndarray) -> np.ndarray:
        """ROI 마스크 생성"""
        height, width = shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, vertices, 255)
        return mask

    @staticmethod
    def average_lane_lines(lines: List[Tuple[int, int, int, int]],
                           height: int,
                           top_ratio: float = 0.6) -> Tuple[int, int, int, int] | None:
        """여러 선분을 평균내어 하나의 차선으로"""
        if not lines:
            return None

        x_coords = []
        y_coords = []

        for x1, y1, x2, y2 in lines:
            x_coords.extend([x1, x2])
            y_coords.extend([y1, y2])

        if len(x_coords) < 2:
            return None

        poly = np.polyfit(y_coords, x_coords, 1)

        y1 = height
        y2 = int(height * top_ratio)
        x1 = int(poly[0] * y1 + poly[1])
        x2 = int(poly[0] * y2 + poly[1])

        return (x1, y1, x2, y2)
