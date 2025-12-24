# ============================================================================
# src/ui/widgets/progress_bar.py
# 미디어 프로그레스 바
# ============================================================================

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QMouseEvent

from ...config.constants import APP_CONST, COLOR


class MediaProgressBar(QWidget):
    """클릭 가능한 미디어 프로그레스 바"""

    seek_requested = Signal(int)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(APP_CONST.PROGRESS_BAR_HEIGHT)
        self.setMouseTracking(True)

        self._current_frame = 0
        self._total_frames = 0
        self._hover_position = -1
        self._is_hovering = False
        self._fps = APP_CONST.DEFAULT_FPS

        # 색상
        self.bg_color = QColor(COLOR.BG_MEDIUM)
        self.progress_start = QColor(COLOR.PROGRESS_START)
        self.progress_end = QColor(COLOR.PROGRESS_END)
        self.hover_color = QColor(255, 255, 255, 40)
        self.handle_color = QColor(COLOR.TEXT_PRIMARY)
        self.border_color = QColor(COLOR.BORDER_COLOR)

        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)

        # 현재 시간
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet(f"""
            color: {COLOR.TEXT_PRIMARY}; 
            font-size: 13px; 
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        self.time_label.setFixedWidth(55)
        layout.addWidget(self.time_label)

        layout.addStretch()

        # 전체 시간
        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet(f"""
            color: {COLOR.TEXT_SECONDARY}; 
            font-size: 13px;
            font-family: 'Segoe UI', Arial;
        """)
        self.duration_label.setFixedWidth(55)
        layout.addWidget(self.duration_label)

    def set_total_frames(self, total_frames: int, fps: float):
        """전체 프레임 설정"""
        self._total_frames = total_frames
        self._fps = fps
        duration_sec = total_frames / fps if fps > 0 else 0
        self.duration_label.setText(self._format_time(duration_sec))
        self.update()

    def set_current_frame(self, frame_number: int):
        """현재 프레임 설정"""
        self._current_frame = frame_number
        current_sec = frame_number / self._fps if self._fps > 0 else 0
        self.time_label.setText(self._format_time(current_sec))
        self.update()

    def reset(self):
        """초기화"""
        self._current_frame = 0
        self._total_frames = 0
        self._hover_position = -1
        self.time_label.setText("00:00")
        self.duration_label.setText("00:00")
        self.update()

    def _format_time(self, seconds: float) -> str:
        """시간 포맷팅"""
        if seconds < 0:
            return "00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _get_progress_rect(self):
        """프로그레스 바 영역"""
        margin = 15
        return self.rect().adjusted(margin, 25, -margin, -8)

    def paintEvent(self, event):
        """그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        progress_rect = self._get_progress_rect()
        bar_height = 8
        y_center = progress_rect.center().y()
        bar_rect = progress_rect.adjusted(
            0, y_center - bar_height // 2,
            0, y_center + bar_height // 2
        )

        # 배경
        painter.setPen(QPen(self.border_color, 1))
        painter.setBrush(QBrush(self.bg_color))
        painter.drawRoundedRect(bar_rect, 4, 4)

        # 호버 효과
        if self._is_hovering and self._hover_position >= 0:
            hover_width = int(bar_rect.width() * self._hover_position)
            hover_rect = bar_rect.adjusted(
                0, 0, hover_width - bar_rect.width(), 0
            )
            painter.setBrush(QBrush(self.hover_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(hover_rect, 4, 4)

        # 진행 바
        if self._total_frames > 0:
            progress_ratio = self._current_frame / self._total_frames
            progress_width = int(bar_rect.width() * progress_ratio)

            if progress_width > 0:
                progress_rect_filled = bar_rect.adjusted(
                    0, 0, progress_width - bar_rect.width(), 0
                )

                gradient = QLinearGradient(
                    progress_rect_filled.left(), 0,
                    progress_rect_filled.right(), 0
                )
                gradient.setColorAt(0, self.progress_start)
                gradient.setColorAt(1, self.progress_end)

                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(progress_rect_filled, 4, 4)

                # 핸들
                if self._is_hovering:
                    handle_x = progress_rect_filled.right()
                    handle_y = bar_rect.center().y()
                    handle_radius = 10

                    painter.setBrush(QBrush(self.handle_color))
                    painter.setPen(QPen(QColor(20, 20, 25), 3))
                    painter.drawEllipse(
                        QPoint(handle_x, handle_y),
                        handle_radius, handle_radius
                    )

    def mouseMoveEvent(self, event: QMouseEvent):
        """마우스 이동"""
        progress_rect = self._get_progress_rect()
        if progress_rect.contains(event.pos()):
            self._is_hovering = True
            relative_x = event.pos().x() - progress_rect.left()
            self._hover_position = max(0.0, min(1.0,
                                                relative_x / progress_rect.width()))
        else:
            self._is_hovering = False
            self._hover_position = -1
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """마우스 클릭"""
        if event.button() == Qt.MouseButton.LeftButton:
            progress_rect = self._get_progress_rect()
            if progress_rect.contains(event.pos()) and self._total_frames > 0:
                relative_x = event.pos().x() - progress_rect.left()
                click_ratio = max(0.0, min(1.0,
                                           relative_x / progress_rect.width()))
                new_frame = int(self._total_frames * click_ratio)
                self.seek_requested.emit(new_frame)

    def leaveEvent(self, event):
        """마우스 벗어남"""
        self._is_hovering = False
        self._hover_position = -1
        self.update()
