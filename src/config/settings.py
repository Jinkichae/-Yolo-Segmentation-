# ============================================================================
# src/config/settings.py
# 설정 관리자
# ============================================================================

from typing import Any, Dict
from dataclasses import dataclass, asdict


@dataclass
class DefaultSettings:
    """기본 설정값"""
    detection_enabled: bool = True
    segmentation_enabled: bool = False
    lane_detection_enabled: bool = True
    show_labels: bool = True
    show_distance: bool = True
    confidence_threshold: float = 0.5
    frame_skip: int = 0
    use_gpu: bool = True


class SettingsManager:
    """설정 관리자 (싱글톤)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        default = DefaultSettings()
        self._settings: Dict[str, Any] = asdict(default)
        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def update(self, **kwargs) -> None:
        self._settings.update(kwargs)

    def reset(self) -> None:
        default = DefaultSettings()
        self._settings = asdict(default)

    def to_dict(self) -> Dict[str, Any]:
        return self._settings.copy()
