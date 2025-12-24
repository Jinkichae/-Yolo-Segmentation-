# ============================================================================
# src/core/video_processor.py
# 비디오 처리 스레드 (완전 수정 버전)
# ============================================================================

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from collections import deque
from typing import Optional
import time

from ..config.settings import SettingsManager
from ..models.stats import DetectionStats
from ..models.detection import Detection, LaneLines
from .model_manager import ModelManager
from .detection_engine import DetectionEngine
from .lane_detector import LaneDetector
from ..utils.drawing import DrawingUtils
from ..utils.performance import PerformanceMonitor, Timer


class VideoProcessor(QThread):
    """비디오 처리 스레드"""

    # Signals
    frame_ready = Signal(np.ndarray, list, int, DetectionStats)
    video_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()

        # 의존성 주입
        self.model_manager = ModelManager()
        self.detection_engine = DetectionEngine(self.model_manager)
        self.lane_detector = LaneDetector()
        self.settings = SettingsManager()
        self.performance_monitor = PerformanceMonitor()

        # 비디오 캡처
        self.video_path: Optional[str] = None
        self.cap: Optional[cv2.VideoCapture] = None

        # 재생 상태
        self.is_running = False
        self.is_paused = False
        self.current_frame_number = 0
        self.total_frames = 0
        self.fps = 30.0

        # Seek 제어
        self.seek_to = -1
        self.mutex = QMutex()

        # 프레임 버퍼
        self.frame_buffer = deque(maxlen=5)

    def load_video(self, video_path: str) -> bool:
        """비디오 로드"""
        try:
            self.video_path = video_path
            self.cap = cv2.VideoCapture(video_path)

            if not self.cap.isOpened():
                self.error_occurred.emit(f"비디오를 열 수 없습니다: {video_path}")
                return False

            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.current_frame_number = 0

            # 캐시 초기화
            self.lane_detector.reset()
            self.performance_monitor.reset()

            print(f"비디오 로드 성공: {self.total_frames} 프레임, {self.fps:.2f} FPS")
            return True

        except Exception as e:
            self.error_occurred.emit(f"비디오 로드 실패: {str(e)}")
            return False

    def seek_to_frame(self, frame_number: int) -> None:
        """특정 프레임으로 이동"""
        with QMutexLocker(self.mutex):
            self.seek_to = frame_number

    def process_frame(self, frame: np.ndarray) -> tuple:
        """프레임 처리"""
        if frame is None:
            return frame, [], DetectionStats(), LaneLines()

        timer = Timer()
        stats = DetectionStats()

        with timer:
            # 1. 차선 감지
            lanes = self._process_lanes(frame)

            # 2. 객체 탐지
            detections, detection_stats = self._process_detections(frame)
            stats = detection_stats

            # 3. Segmentation
            if self.settings.get('segmentation_enabled'):
                frame = self.detection_engine.apply_segmentation(frame)

            # 4. 시각화
            self._visualize_results(frame, detections, lanes)

        stats.processing_time = timer.get_elapsed_ms()

        return frame, detections, stats, lanes

    def _process_lanes(self, frame: np.ndarray) -> LaneLines:
        """차선 처리"""
        if not self.settings.get('lane_detection_enabled'):
            return LaneLines()

        lanes = self.lane_detector.detect(frame)
        DrawingUtils.draw_lane_lines(frame, lanes)
        DrawingUtils.draw_lane_warning(frame, lanes)

        return lanes

    def _process_detections(self, frame: np.ndarray) -> tuple:
        """객체 탐지 처리"""
        return self.detection_engine.detect_objects(frame)

    def _visualize_results(self, frame: np.ndarray,
                           detections: list,
                           lanes: LaneLines) -> None:
        """결과 시각화"""
        show_labels = self.settings.get('show_labels', True)
        show_distance = self.settings.get('show_distance', True)

        for detection in detections:
            DrawingUtils.draw_detection_box(
                frame, detection, show_labels, show_distance
            )

    def run(self):
        """스레드 실행"""
        self.is_running = True

        # 모델 로드
        if self.settings.get('detection_enabled'):
            self.model_manager.load_detection_model()

        if not self.cap or not self.cap.isOpened():
            self.error_occurred.emit("비디오가 로드되지 않았습니다")
            return

        frame_delay = int(1000 / self.fps) if self.fps > 0 else 33
        frame_count = 0
        frame_skip = self.settings.get('frame_skip', 0)

        while self.is_running:
            # 일시정지
            if self.is_paused:
                self.msleep(100)
                continue

            # Seek 처리
            self._handle_seek()

            # 프레임 읽기
            ret, frame = self.cap.read()

            if not ret:
                self.video_finished.emit()
                break

            # 프레임 스킵
            if frame_skip > 0 and frame_count % (frame_skip + 1) != 0:
                frame_count += 1
                self.current_frame_number += 1
                continue

            frame_count += 1

            # 프레임 처리
            processed_frame, detections, stats, lanes = self.process_frame(frame)

            # FPS 계산
            stats.fps = self.performance_monitor.update_fps()

            # 결과 전송
            self.frame_ready.emit(
                processed_frame,
                detections,
                self.current_frame_number,
                stats
            )

            self.current_frame_number += 1

            # FPS 조절
            self.msleep(frame_delay)

    def _handle_seek(self) -> None:
        """Seek 요청 처리"""
        with QMutexLocker(self.mutex):
            if self.seek_to >= 0:
                if self.cap:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_to)
                    self.current_frame_number = self.seek_to
                    self.lane_detector.reset()
                self.seek_to = -1

    def stop(self) -> None:
        """스레드 정지"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def cleanup(self) -> None:
        """리소스 정리"""
        self.stop()
        self.model_manager.unload_models()