# ============================================================================
# src/config/constants.py
# 애플리케이션 전역 상수 (SSOT)
# ============================================================================

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AppConstants:
    """애플리케이션 상수 (불변)"""

    # 애플리케이션 정보
    APP_NAME: str = "자율주행 비디오 분석 시스템"
    APP_VERSION: str = "2.0.0"

    # 비디오 설정
    DEFAULT_VIDEO_FILE: str = "screen_1766557465783.mp4"
    SUPPORTED_VIDEO_FORMATS: Tuple[str, ...] = (".mp4", ".avi", ".mov", ".mkv")

    # YOLO 모델
    DETECTION_MODEL: str = "yolov8n.pt"
    SEGMENTATION_MODEL: str = "yolov8n-seg.pt"

    # 성능 최적화
    DEFAULT_FPS: int = 30
    MAX_FRAME_BUFFER: int = 5
    FPS_UPDATE_INTERVAL: float = 1.0

    # 거리 추정
    FOCAL_LENGTH: float = 800.0
    KNOWN_WIDTH: float = 1.8

    # 거리 임계값
    DANGER_DISTANCE: float = 5.0
    WARNING_DISTANCE: float = 10.0

    # 차선 감지
    LANE_ROI_TOP: float = 0.6
    LANE_ROI_LEFT: float = 0.1
    LANE_ROI_RIGHT: float = 0.9

    CANNY_LOW_THRESHOLD: int = 50
    CANNY_HIGH_THRESHOLD: int = 150

    HOUGH_RHO: int = 2
    HOUGH_THRESHOLD: int = 50
    HOUGH_MIN_LINE_LENGTH: int = 40
    HOUGH_MAX_LINE_GAP: int = 150

    MIN_SLOPE: float = 0.5
    LANE_OFFSET_THRESHOLD: int = 50

    # UI 설정
    WINDOW_WIDTH: int = 1600
    WINDOW_HEIGHT: int = 950
    VIDEO_MIN_WIDTH: int = 900
    VIDEO_MIN_HEIGHT: int = 600
    STATS_MIN_WIDTH: int = 280
    STATS_MAX_WIDTH: int = 350

    PROGRESS_BAR_HEIGHT: int = 70


@dataclass(frozen=True)
class ColorScheme:
    """색상 테마"""

    # 메인 배경
    BG_DARK: str = "#1e1e28"
    BG_MEDIUM: str = "#2a2a35"
    BG_LIGHT: str = "#3a3a45"

    # 테두리
    BORDER_COLOR: str = "#4a4a55"
    BORDER_LIGHT: str = "#5a5a65"

    # 텍스트
    TEXT_PRIMARY: str = "#ffffff"
    TEXT_SECONDARY: str = "#b0b0b0"
    TEXT_DISABLED: str = "#666666"

    # 상태 색상
    SUCCESS_COLOR: str = "#48bb78"
    WARNING_COLOR: str = "#f6ad55"
    DANGER_COLOR: str = "#ff4444"
    INFO_COLOR: str = "#4299e1"

    # 프로그레스 바
    PROGRESS_START: str = "#4299e1"
    PROGRESS_END: str = "#48bb78"

    # 차선 색상 (BGR)
    LANE_LEFT: Tuple[int, int, int] = (0, 0, 255)
    LANE_RIGHT: Tuple[int, int, int] = (255, 0, 0)
    LANE_AREA: Tuple[int, int, int] = (0, 255, 0)

    # 탐지 박스 색상 (BGR)
    DANGER_BOX: Tuple[int, int, int] = (0, 0, 255)
    WARNING_BOX: Tuple[int, int, int] = (0, 165, 255)
    SAFE_BOX: Tuple[int, int, int] = (0, 255, 0)


# 싱글톤 인스턴스 생성
APP_CONST = AppConstants()
COLOR = ColorScheme()
