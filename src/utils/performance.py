# ============================================================================
# src/utils/performance.py
# 성능 측정 유틸리티
# ============================================================================

import time
from typing import Optional


class PerformanceMonitor:
    """성능 모니터"""

    FPS_UPDATE_INTERVAL = 1.0  # 1초마다 FPS 업데이트 (클래스 상수로 직접 정의)

    def __init__(self):
        self.last_fps_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0

    def update_fps(self) -> float:
        """FPS 업데이트"""
        self.fps_counter += 1
        current_time = time.time()

        elapsed = current_time - self.last_fps_time

        if elapsed >= self.FPS_UPDATE_INTERVAL:  # ✅ APP_CONST 대신 클래스 상수 사용
            self.current_fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.last_fps_time = current_time

        return self.current_fps

    def reset(self) -> None:
        """초기화"""
        self.last_fps_time = time.time()
        self.fps_counter = 0
        self.current_fps = 0.0


class Timer:
    """간단한 타이머 (컨텍스트 매니저)"""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.elapsed: float = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.elapsed = (time.time() - self.start_time) * 1000  # ms

    def get_elapsed_ms(self) -> float:
        """경과 시간 (밀리초)"""
        return self.elapsed