# ============================================================================
# src/core/model_manager.py
# YOLO 모델 관리자
# ============================================================================

from ultralytics import YOLO
from typing import Optional
import torch


class ModelManager:
    """YOLO 모델 관리자 (싱글톤)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._detection_model: Optional[YOLO] = None
        self._segmentation_model: Optional[YOLO] = None
        self._device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self._initialized = True

        # 모델 파일명
        self.detection_model_name = 'yolov8n.pt'
        self.segmentation_model_name = 'yolov8n-seg.pt'

        print(f"ModelManager initialized with device: {self._device}")

    @property
    def device(self) -> str:
        """현재 디바이스"""
        return self._device

    @property
    def detection_model(self) -> Optional[YOLO]:
        """Detection 모델"""
        return self._detection_model

    @property
    def segmentation_model(self) -> Optional[YOLO]:
        """Segmentation 모델"""
        return self._segmentation_model

    def load_detection_model(self, force_reload: bool = False) -> YOLO:
        """Detection 모델 로드"""
        if self._detection_model is not None and not force_reload:
            return self._detection_model

        print(f"Loading detection model: {self.detection_model_name}")
        self._detection_model = YOLO(self.detection_model_name)

        if self._device.startswith('cuda'):
            self._detection_model.to(self._device)

        return self._detection_model

    def load_segmentation_model(self, force_reload: bool = False) -> YOLO:
        """Segmentation 모델 로드"""
        if self._segmentation_model is not None and not force_reload:
            return self._segmentation_model

        print(f"Loading segmentation model: {self.segmentation_model_name}")
        self._segmentation_model = YOLO(self.segmentation_model_name)

        if self._device.startswith('cuda'):
            self._segmentation_model.to(self._device)

        return self._segmentation_model

    def unload_models(self) -> None:
        """모델 언로드 (메모리 해제)"""
        self._detection_model = None
        self._segmentation_model = None

        if torch.cuda.is_available():
            torch.cuda.empty_cache()