# ============================================================================
# src/utils/drawing.py
# 그리기 유틸리티
# ============================================================================

import cv2
import numpy as np
from typing import Tuple

from ..models.detection import Detection, LaneLines


class DrawingUtils:
    """그리기 유틸리티"""

    # 색상 상수 (BGR)
    DANGER_COLOR = (0, 0, 255)
    WARNING_COLOR = (0, 165, 255)
    SAFE_COLOR = (0, 255, 0)
    LANE_LEFT_COLOR = (0, 0, 255)
    LANE_RIGHT_COLOR = (255, 0, 0)
    LANE_AREA_COLOR = (0, 255, 0)

    @staticmethod
    def draw_detection_box(frame: np.ndarray,
                           detection: Detection,
                           show_label: bool = True,
                           show_distance: bool = True,
                           danger_threshold: float = 5.0,
                           warning_threshold: float = 10.0) -> None:
        """탐지 박스 그리기"""
        bbox = detection.bbox.astype(int)

        # 거리에 따른 색상
        if detection.distance < danger_threshold:
            color = DrawingUtils.DANGER_COLOR
        elif detection.distance < warning_threshold:
            color = DrawingUtils.WARNING_COLOR
        else:
            color = DrawingUtils.SAFE_COLOR

        # 박스 그리기
        cv2.rectangle(frame,
                      (bbox[0], bbox[1]),
                      (bbox[2], bbox[3]),
                      color, 2)

        # 레이블
        if show_label:
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            if show_distance and detection.distance < 100:
                label += f" ({detection.distance:.1f}m)"

            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

            cv2.rectangle(frame,
                          (bbox[0], bbox[1] - text_height - 10),
                          (bbox[0] + text_width, bbox[1]),
                          color, -1)

            cv2.putText(frame, label,
                        (bbox[0], bbox[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)

    @staticmethod
    def draw_lane_lines(frame: np.ndarray, lanes: LaneLines) -> np.ndarray:
        """차선 그리기"""
        overlay = frame.copy()

        # 차선 영역 채우기
        if lanes.is_complete():
            points = np.array([
                [lanes.left_lane[0], lanes.left_lane[1]],
                [lanes.left_lane[2], lanes.left_lane[3]],
                [lanes.right_lane[2], lanes.right_lane[3]],
                [lanes.right_lane[0], lanes.right_lane[1]]
            ], dtype=np.int32)

            cv2.fillPoly(overlay, [points], DrawingUtils.LANE_AREA_COLOR)
            cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)

        # 왼쪽 차선
        if lanes.left_lane is not None:
            cv2.line(frame,
                     (lanes.left_lane[0], lanes.left_lane[1]),
                     (lanes.left_lane[2], lanes.left_lane[3]),
                     DrawingUtils.LANE_LEFT_COLOR, 8)

        # 오른쪽 차선
        if lanes.right_lane is not None:
            cv2.line(frame,
                     (lanes.right_lane[0], lanes.right_lane[1]),
                     (lanes.right_lane[2], lanes.right_lane[3]),
                     DrawingUtils.LANE_RIGHT_COLOR, 8)

        return frame

    @staticmethod
    def draw_lane_warning(frame: np.ndarray, lanes: LaneLines,
                          offset_threshold: int = 50,
                          top_ratio: float = 0.6) -> None:
        """차선 이탈 경고"""
        if not lanes.is_complete():
            return

        offset = lanes.get_center_offset(frame.shape[1])

        if abs(offset) > offset_threshold:
            warning_text = f"차선 이탈! (오프셋: {offset}px)"
            cv2.putText(frame, warning_text,
                        (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, DrawingUtils.DANGER_COLOR, 3)

        # 차량 중심선
        center_x = frame.shape[1] // 2
        cv2.line(frame,
                 (center_x, frame.shape[0]),
                 (center_x, int(frame.shape[0] * top_ratio)),
                 (255, 255, 255), 2)