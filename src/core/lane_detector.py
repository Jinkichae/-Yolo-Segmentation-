# ============================================================================
# src/core/lane_detector.py
# 차선 감지 엔진
# ============================================================================

import cv2
import numpy as np
from typing import Optional, Tuple

from ..models.detection import LaneLines
from ..utils.geometry import GeometryUtils


class LaneDetector:
    """차선 감지 엔진"""

    def __init__(self):
        self._roi_mask: Optional[np.ndarray] = None
        self._roi_vertices: Optional[np.ndarray] = None
        self._frame_shape: Optional[Tuple[int, int]] = None

        # 설정값
        self.canny_low = 50
        self.canny_high = 150
        self.hough_rho = 2
        self.hough_threshold = 50
        self.hough_min_line_length = 40
        self.hough_max_line_gap = 150
        self.min_slope = 0.5

    def detect(self, frame: np.ndarray) -> LaneLines:
        """차선 감지"""
        # ROI 마스크 초기화 (프레임 크기 변경 시)
        if (self._frame_shape is None or
                self._frame_shape != frame.shape[:2]):
            self._initialize_roi(frame.shape)

        # 전처리
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, self.canny_low, self.canny_high)

        # ROI 적용
        masked_edges = cv2.bitwise_and(edges, self._roi_mask)

        # Hough Line Transform
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=self.hough_rho,
            theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.hough_min_line_length,
            maxLineGap=self.hough_max_line_gap
        )

        if lines is None:
            return LaneLines()

        # 좌/우 차선 분리
        left_lines, right_lines = self._separate_lanes(lines)

        # 차선 평균 및 외삽
        height = frame.shape[0]
        left_lane = GeometryUtils.average_lane_lines(left_lines, height)
        right_lane = GeometryUtils.average_lane_lines(right_lines, height)

        return LaneLines(left_lane=left_lane, right_lane=right_lane)

    def _initialize_roi(self, shape: Tuple[int, ...]) -> None:
        """ROI 초기화"""
        height, width = shape[:2]
        self._frame_shape = (height, width)

        self._roi_vertices = GeometryUtils.create_roi_vertices(width, height)
        self._roi_mask = GeometryUtils.create_roi_mask(shape, self._roi_vertices)

    def _separate_lanes(self, lines: np.ndarray) -> Tuple[list, list]:
        """좌/우 차선 분리"""
        left_lines = []
        right_lines = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            if x2 == x1:
                continue

            slope = (y2 - y1) / (x2 - x1)

            if abs(slope) < self.min_slope:
                continue

            if slope < 0:
                left_lines.append((x1, y1, x2, y2))
            else:
                right_lines.append((x1, y1, x2, y2))

        return left_lines, right_lines

    def reset(self) -> None:
        """캐시 초기화"""
        self._roi_mask = None
        self._roi_vertices = None
        self._frame_shape = None
