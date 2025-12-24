# ============================================================================
# src/ui/widgets/stats_widget.py
# 통계 위젯
# ============================================================================

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel
from PySide6.QtCore import Qt

from ...config.constants import COLOR
from ...models.stats import DetectionStats


class StatsWidget(QFrame):
    """실시간 통계 대시보드"""

    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR.BG_MEDIUM};
                border-radius: 8px;
                border: 1px solid {COLOR.BORDER_COLOR};
            }}
        """)
        self._init_ui()

    def _init_ui(self):
        """UI 초기화"""
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 제목
        title = QLabel("📊 탐지 통계")
        title.setStyleSheet(f"""
            color: {COLOR.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        layout.addWidget(title, 0, 0, 1, 2)

        # 통계 레이블들
        self.fps_label = self._create_stat_label("FPS:", "0.0")
        self.objects_label = self._create_stat_label("객체:", "0")
        self.danger_label = self._create_stat_label("위험:", "0")
        self.time_label = self._create_stat_label("처리:", "0ms")

        layout.addWidget(self.fps_label, 1, 0)
        layout.addWidget(self.objects_label, 1, 1)
        layout.addWidget(self.danger_label, 2, 0)
        layout.addWidget(self.time_label, 2, 1)

        # 상세 정보
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(f"""
            color: {COLOR.TEXT_SECONDARY};
            font-size: 11px;
            font-family: 'Segoe UI', Arial;
        """)
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label, 3, 0, 1, 2)

    def _create_stat_label(self, prefix: str, value: str) -> QLabel:
        """통계 레이블 생성"""
        label = QLabel(f"{prefix} {value}")
        label.setStyleSheet(f"""
            color: {COLOR.TEXT_PRIMARY};
            font-size: 12px;
            font-family: 'Segoe UI', Arial;
            padding: 5px;
            background-color: {COLOR.BG_LIGHT};
            border-radius: 4px;
        """)
        return label

    def update_stats(self, stats: DetectionStats):
        """통계 업데이트"""
        self.fps_label.setText(f"FPS: {stats.fps:.1f}")
        self.objects_label.setText(f"객체: {stats.total_objects}")

        # 위험 객체 강조
        if stats.dangerous_objects > 0:
            self.danger_label.setText(f"⚠️ 위험: {stats.dangerous_objects}")
            self.danger_label.setStyleSheet(f"""
                color: {COLOR.DANGER_COLOR};
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                padding: 5px;
                background-color: #4a2020;
                border-radius: 4px;
            """)
        else:
            self.danger_label.setText(f"위험: {stats.dangerous_objects}")
            self.danger_label.setStyleSheet(f"""
                color: {COLOR.TEXT_PRIMARY};
                font-size: 12px;
                font-family: 'Segoe UI', Arial;
                padding: 5px;
                background-color: {COLOR.BG_LIGHT};
                border-radius: 4px;
            """)

        self.time_label.setText(f"처리: {stats.processing_time:.0f}ms")

        # 상세 정보
        if stats.object_counts:
            detail_text = ", ".join([
                f"{k}: {v}" for k, v in stats.object_counts.items()
            ])
            self.detail_label.setText(detail_text)
        else:
            self.detail_label.setText("탐지된 객체 없음")