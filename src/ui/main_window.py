# ============================================================================
# src/ui/main_window.py
# 메인 윈도우
# ============================================================================

import sys
import cv2
import numpy as np
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QCheckBox, QGroupBox,
    QSpinBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from ..config.constants import APP_CONST, COLOR
from ..config.settings import SettingsManager
from ..core.video_processor import VideoProcessor
from ..models.stats import DetectionStats
from .widgets.progress_bar import MediaProgressBar
from .widgets.stats_widget import StatsWidget
from .styles.theme import AppTheme


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self, video_path: str = APP_CONST.DEFAULT_VIDEO_FILE):
        super().__init__()

        self.setWindowTitle(f"🚗 {APP_CONST.APP_NAME} v{APP_CONST.APP_VERSION}")
        self.setGeometry(100, 100,
                         APP_CONST.WINDOW_WIDTH,
                         APP_CONST.WINDOW_HEIGHT)

        # 설정 관리자
        self.settings = SettingsManager()

        # 비디오 프로세서
        self.video_processor = VideoProcessor()
        self.video_processor.frame_ready.connect(self.on_frame_ready)
        self.video_processor.video_finished.connect(self.on_video_finished)
        self.video_processor.error_occurred.connect(self.on_error)

        # 현재 pixmap 캐싱
        self.current_pixmap = None
        self.video_path = video_path

        # UI 초기화
        self.setStyleSheet(AppTheme.get_main_stylesheet())
        self.init_ui()

        # 초기 비디오 로드
        if Path(video_path).exists():
            QTimer.singleShot(100, lambda: self.load_and_play_video(video_path))

    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 상단 컨트롤
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel)

        # 중앙 영역 (스플리터)
        splitter = self._create_center_splitter()
        main_layout.addWidget(splitter, stretch=1)

        # 프로그레스 바
        self.progress_bar = MediaProgressBar()
        self.progress_bar.seek_requested.connect(self.on_seek_requested)
        main_layout.addWidget(self.progress_bar)

        # 하단 상태바
        self.status_label = QLabel("📂 비디오를 열어주세요")
        self.status_label.setStyleSheet(f"""
            color: {COLOR.TEXT_SECONDARY};
            font-size: 12px;
            padding: 5px;
        """)
        main_layout.addWidget(self.status_label)

    def _create_control_panel(self) -> QGroupBox:
        """컨트롤 패널 생성"""
        group = QGroupBox("🎮 비디오 컨트롤")
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # 파일 열기
        self.open_btn = QPushButton("📁 열기")
        self.open_btn.setFixedWidth(90)
        self.open_btn.clicked.connect(self.open_video)
        layout.addWidget(self.open_btn)

        # 재생/일시정지
        self.play_btn = QPushButton("▶ 재생")
        self.play_btn.setFixedWidth(100)
        self.play_btn.clicked.connect(self.toggle_play)
        layout.addWidget(self.play_btn)

        # 정지
        self.stop_btn = QPushButton("⏹ 정지")
        self.stop_btn.setFixedWidth(90)
        self.stop_btn.clicked.connect(self.stop_video)
        layout.addWidget(self.stop_btn)

        layout.addSpacing(20)

        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet(f"background-color: {COLOR.BORDER_COLOR};")
        layout.addWidget(separator)

        layout.addSpacing(10)

        # Detection
        self.detection_check = QCheckBox("🔍 Object Detection")
        self.detection_check.setChecked(
            self.settings.get('detection_enabled', True)
        )
        self.detection_check.stateChanged.connect(
            lambda: self.settings.set('detection_enabled',
                                      self.detection_check.isChecked())
        )
        layout.addWidget(self.detection_check)

        # Segmentation
        self.segmentation_check = QCheckBox("🎨 Segmentation")
        self.segmentation_check.setChecked(
            self.settings.get('segmentation_enabled', False)
        )
        self.segmentation_check.stateChanged.connect(self._on_segmentation_changed)
        layout.addWidget(self.segmentation_check)

        # 차선 감지
        self.lane_check = QCheckBox("🛣️ 차선 감지")
        self.lane_check.setChecked(
            self.settings.get('lane_detection_enabled', True)
        )
        self.lane_check.stateChanged.connect(
            lambda: self.settings.set('lane_detection_enabled',
                                      self.lane_check.isChecked())
        )
        layout.addWidget(self.lane_check)

        layout.addSpacing(10)

        # 레이블 표시
        self.label_check = QCheckBox("🏷️ 레이블")
        self.label_check.setChecked(self.settings.get('show_labels', True))
        self.label_check.stateChanged.connect(
            lambda: self.settings.set('show_labels',
                                      self.label_check.isChecked())
        )
        layout.addWidget(self.label_check)

        # 거리 표시
        self.distance_check = QCheckBox("📏 거리")
        self.distance_check.setChecked(self.settings.get('show_distance', True))
        self.distance_check.stateChanged.connect(
            lambda: self.settings.set('show_distance',
                                      self.distance_check.isChecked())
        )
        layout.addWidget(self.distance_check)

        layout.addSpacing(10)

        # 신뢰도
        layout.addWidget(QLabel("신뢰도:"))
        self.conf_spinbox = QSpinBox()
        self.conf_spinbox.setRange(10, 90)
        self.conf_spinbox.setValue(50)
        self.conf_spinbox.setSuffix("%")
        self.conf_spinbox.setFixedWidth(70)
        self.conf_spinbox.valueChanged.connect(
            lambda v: self.settings.set('confidence_threshold', v / 100)
        )
        layout.addWidget(self.conf_spinbox)

        layout.addSpacing(10)

        # 프레임 스킵
        layout.addWidget(QLabel("프레임 스킵:"))
        self.skip_spinbox = QSpinBox()
        self.skip_spinbox.setRange(0, 5)
        self.skip_spinbox.setValue(0)
        self.skip_spinbox.setFixedWidth(60)
        self.skip_spinbox.valueChanged.connect(
            lambda v: self.settings.set('frame_skip', v)
        )
        layout.addWidget(self.skip_spinbox)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def _create_center_splitter(self) -> QSplitter:
        """중앙 스플리터 생성"""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 비디오 디스플레이
        video_container = QWidget()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(f"""
            background-color: #000000;
            border: 2px solid {COLOR.BORDER_COLOR};
            border-radius: 8px;
        """)
        self.video_label.setMinimumSize(
            APP_CONST.VIDEO_MIN_WIDTH,
            APP_CONST.VIDEO_MIN_HEIGHT
        )
        video_layout.addWidget(self.video_label)

        splitter.addWidget(video_container)

        # 통계 패널
        self.stats_widget = StatsWidget()
        self.stats_widget.setMinimumWidth(APP_CONST.STATS_MIN_WIDTH)
        self.stats_widget.setMaximumWidth(APP_CONST.STATS_MAX_WIDTH)
        splitter.addWidget(self.stats_widget)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        return splitter

    def _on_segmentation_changed(self):
        """Segmentation 옵션 변경"""
        enabled = self.segmentation_check.isChecked()
        self.settings.set('segmentation_enabled', enabled)

        if enabled:
            QTimer.singleShot(0,
                              self.video_processor.model_manager.load_segmentation_model
                              )

    def load_video(self, file_path: str) -> bool:
        """비디오 로드"""
        if not Path(file_path).exists():
            self.status_label.setText(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return False

        # 기존 재생 중지
        if self.video_processor.is_running:
            self.video_processor.stop()
            self.video_processor.wait()

        self.video_path = file_path

        if self.video_processor.load_video(file_path):
            self.progress_bar.set_total_frames(
                self.video_processor.total_frames,
                self.video_processor.fps
            )

            self.status_label.setText(f"✅ 로드 완료: {Path(file_path).name}")
            self.play_btn.setEnabled(True)
            return True
        else:
            self.status_label.setText("❌ 비디오를 로드할 수 없습니다")
            return False

    def load_and_play_video(self, file_path: str):
        """비디오 로드 및 자동 재생"""
        if self.load_video(file_path):
            QTimer.singleShot(200, self.auto_play)

    def auto_play(self):
        """자동 재생"""
        if not self.video_processor.is_running:
            self.video_processor.start()
            self.play_btn.setText("⏸ 일시정지")
            self.status_label.setText(f"🎬 재생 중: {Path(self.video_path).name}")

    def open_video(self):
        """비디오 파일 열기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "비디오 파일 선택", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )

        if file_path:
            self.load_video(file_path)

    def toggle_play(self):
        """재생/일시정지"""
        if not self.video_processor.is_running:
            self.video_processor.start()
            self.play_btn.setText("⏸ 일시정지")
        else:
            self.video_processor.is_paused = not self.video_processor.is_paused
            if self.video_processor.is_paused:
                self.play_btn.setText("▶ 재생")
            else:
                self.play_btn.setText("⏸ 일시정지")

    def stop_video(self):
        """비디오 정지"""
        if self.video_processor.is_running:
            self.video_processor.stop()
            self.video_processor.wait()

        self.play_btn.setText("▶ 재생")
        self.progress_bar.set_current_frame(0)
        self.video_label.clear()
        self.video_label.setText("⏹ 비디오가 정지되었습니다")

        # 비디오 재로드
        if Path(self.video_path).exists():
            self.video_processor.load_video(self.video_path)

    def on_frame_ready(self, processed_frame: np.ndarray,
                       detections: list,
                       frame_number: int,
                       stats: DetectionStats):
        """처리된 프레임 표시"""
        # BGR to RGB
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        q_image = QImage(rgb_frame.data, w, h, bytes_per_line,
                         QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # 비율 유지하며 크기 조정
        label_size = self.video_label.size()
        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

        # 프로그레스 바 업데이트
        self.progress_bar.set_current_frame(frame_number)

        # 통계 업데이트
        self.stats_widget.update_stats(stats)

    def on_seek_requested(self, frame_number: int):
        """재생 위치 이동"""
        self.video_processor.seek_to_frame(frame_number)

    def on_video_finished(self):
        """비디오 재생 완료"""
        self.play_btn.setText("▶ 재생")
        self.status_label.setText("✅ 비디오 재생 완료 - 자동으로 처음부터 재생합니다")

        # 자동 재재생
        if Path(self.video_path).exists():
            QTimer.singleShot(500, lambda: self.load_and_play_video(self.video_path))

    def on_error(self, error_message: str):
        """에러 처리"""
        self.status_label.setText(f"❌ 에러: {error_message}")
        print(f"Error: {error_message}")

    def resizeEvent(self, event):
        """창 크기 변경"""
        self.current_pixmap = None
        super().resizeEvent(event)

    def closeEvent(self, event):
        """윈도우 닫기"""
        if self.video_processor.is_running:
            self.video_processor.stop()
            self.video_processor.wait()

        self.video_processor.cleanup()
        event.accept()


