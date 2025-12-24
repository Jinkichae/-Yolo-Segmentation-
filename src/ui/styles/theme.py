# ============================================================================
# src/ui/styles/theme.py
# UI 테마 및 스타일
# ============================================================================

from ...config.constants import COLOR


class AppTheme:
    """애플리케이션 테마"""

    @staticmethod
    def get_main_stylesheet() -> str:
        """메인 스타일시트"""
        return f"""
            QMainWindow {{
                background-color: {COLOR.BG_DARK};
            }}
            QGroupBox {{
                background-color: {COLOR.BG_MEDIUM};
                border: 1px solid {COLOR.BORDER_COLOR};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 13px;
                font-weight: bold;
                color: {COLOR.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: {COLOR.BG_LIGHT};
                color: {COLOR.TEXT_PRIMARY};
                border: 1px solid {COLOR.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR.BORDER_COLOR};
                border: 1px solid {COLOR.BORDER_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {COLOR.BG_MEDIUM};
            }}
            QPushButton:disabled {{
                background-color: {COLOR.BG_MEDIUM};
                color: {COLOR.TEXT_DISABLED};
            }}
            QCheckBox {{
                color: {COLOR.TEXT_PRIMARY};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLOR.BORDER_COLOR};
                background-color: {COLOR.BG_MEDIUM};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR.INFO_COLOR};
                border-color: {COLOR.INFO_COLOR};
            }}
            QLabel {{
                color: {COLOR.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial;
            }}
            QSpinBox {{
                background-color: {COLOR.BG_LIGHT};
                color: {COLOR.TEXT_PRIMARY};
                border: 1px solid {COLOR.BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLOR.BORDER_COLOR};
                border-radius: 3px;
            }}
        """