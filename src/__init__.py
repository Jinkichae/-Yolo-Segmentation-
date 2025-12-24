"""자율주행 비디오 분석 시스템"""

__version__ = "2.0.0"

# 순환 import 제거 - lazy import 사용
def get_app_constants():
    from .config.constants import APP_CONST, COLOR
    return APP_CONST, COLOR

def get_settings_manager():
    from .config.settings import SettingsManager
    return SettingsManager()

__all__ = ['get_app_constants', 'get_settings_manager', '__version__']
