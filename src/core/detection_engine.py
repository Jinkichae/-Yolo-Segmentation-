# ============================================================================
# src/core/detection_engine.py
# 객체 탐지 엔진
# ============================================================================

import cv2
import numpy as np
from typing import List, Tuple

from ..models.detection import Detection
from ..models.stats import DetectionStats
from ..utils.geometry import GeometryUtils
from ..config.settings import SettingsManager


class DetectionEngine:
    """객체 탐지 엔진"""

    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.settings = SettingsManager()

    def detect_objects(self, frame: np.ndarray) -> Tuple[List[Detection], DetectionStats]:
        """객체 탐지 실행"""
        detections = []
        stats = DetectionStats()

        if not self.settings.get('detection_enabled'):
            return detections, stats

        model = self.model_manager.detection_model
        if model is None:
            model = self.model_manager.load_detection_model()

        # YOLO 추론
        results = model(
            frame,
            conf=self.settings.get('confidence_threshold', 0.5),
            verbose=False,
            device=self.model_manager.device
        )

        # 결과 파싱
        object_counts = {}

        for result in results:
            boxes = result.boxes
            for box in boxes:
                detection = self._parse_detection(box, model.names)
                detections.append(detection)

                # 통계 수집
                class_name = detection.class_name
                object_counts[class_name] = object_counts.get(class_name, 0) + 1

                if detection.is_dangerous():
                    stats.dangerous_objects += 1

        stats.total_objects = len(detections)
        stats.object_counts = object_counts

        return detections, stats

    def _parse_detection(self, box, class_names: dict) -> Detection:
        """YOLO 박스를 Detection 객체로 변환"""
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        bbox = box.xyxy[0].cpu().numpy()

        bbox_width = bbox[2] - bbox[0]
        distance = GeometryUtils.estimate_distance(bbox_width)

        return Detection(
            class_id=cls_id,
            class_name=class_names[cls_id],
            confidence=conf,
            bbox=bbox,
            distance=distance
        )

    def apply_segmentation(self, frame: np.ndarray) -> np.ndarray:
        """Segmentation 적용"""
        if not self.settings.get('segmentation_enabled'):
            return frame

        model = self.model_manager.segmentation_model
        if model is None:
            model = self.model_manager.load_segmentation_model()

        results = model(
            frame,
            conf=self.settings.get('confidence_threshold', 0.5),
            verbose=False,
            device=self.model_manager.device
        )

        if results[0].masks is None:
            return frame

        # 마스크 오버레이
        masks = results[0].masks.data.cpu().numpy()
        overlay = frame.copy()

        num_masks = len(masks)
        colors = np.random.randint(0, 255, size=(num_masks, 3), dtype=np.uint8)

        for i, mask in enumerate(masks):
            mask_resized = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            mask_bool = mask_resized > 0.5
            overlay[mask_bool] = overlay[mask_bool] * 0.6 + colors[i] * 0.4

        cv2.addWeighted(frame, 0.5, overlay, 0.5, 0, frame)

        return frame
