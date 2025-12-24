# ============================================================================
# run.py (프로젝트 루트)
# 개선된 버전 - 더 유연한 인자 처리
# ============================================================================

"""
자율주행 비디오 분석 시스템 실행 스크립트

사용법:
    python run.py                                    # 기본 비디오 사용
    python run.py video.mp4                          # 비디오 파일만 지정
    python run.py --video video.mp4                  # 명시적 플래그 사용
    python run.py video.mp4 --no-gpu                 # GPU 없이 실행
"""

import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import get_app_constants
APP_CONST, COLOR = get_app_constants()


def parse_arguments():
    """명령행 인자 파싱 (개선 버전)"""
    parser = argparse.ArgumentParser(
        description=f'{APP_CONST.APP_NAME} v{APP_CONST.APP_VERSION}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예제:
  python run.py                                 # 기본 비디오 사용
  python run.py my_video.mp4                    # 비디오만 지정
  python run.py --video my_video.mp4            # 명시적 플래그
  python run.py my_video.mp4 --no-gpu           # GPU 없이 실행
        """
    )

    # 위치 인자로도 받을 수 있게 (선택사항)
    parser.add_argument(
        'video_file',
        nargs='?',
        default=None,
        help='비디오 파일 경로 (선택사항)'
    )

    # --video 플래그로도 받을 수 있게
    parser.add_argument(
        '--video',
        type=str,
        default=None,
        help='비디오 파일 경로'
    )

    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='GPU 사용 안함'
    )

    args = parser.parse_args()

    # video_file과 --video 중 하나라도 지정되면 사용
    if args.video_file:
        args.video = args.video_file
    elif args.video is None:
        args.video = APP_CONST.DEFAULT_VIDEO_FILE

    return args


def main():
    """메인 함수"""
    args = parse_arguments()

    print(f"🚗 {APP_CONST.APP_NAME} v{APP_CONST.APP_VERSION}")
    print(f"📹 비디오: {args.video}")
    print(f"🖥️  GPU: {'비활성' if args.no_gpu else '활성'}")
    print("-" * 50)

    # 설정 적용
    from src.config.settings import SettingsManager
    settings = SettingsManager()

    if args.no_gpu:
        settings.set('use_gpu', False)

    # Qt 애플리케이션
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_CONST.APP_NAME)
    app.setApplicationVersion(APP_CONST.APP_VERSION)

    # 메인 윈도우
    from src.ui.main_window import MainWindow
    window = MainWindow(video_path=args.video)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램이 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

# ============================================================================
# 추가: 빠른 실행 스크립트들
# ============================================================================

# quick_start.bat (Windows)
"""
@echo off
title 자율주행 비디오 분석 시스템
color 0A

echo ========================================
echo  자율주행 비디오 분석 시스템
echo ========================================
echo.

REM 가상환경 활성화
if exist "gpu_venv\Scripts\activate.bat" (
    call gpu_venv\Scripts\activate.bat
    echo [OK] 가상환경 활성화 완료
) else (
    echo [주의] 가상환경을 찾을 수 없습니다
)

echo.
echo 비디오 분석 시작...
echo.

REM 인자가 있으면 그대로 전달, 없으면 기본 실행
python run.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [오류] 프로그램 실행 중 오류 발생
    pause
)
"""

# quick_start.sh (Linux/Mac)
"""
#!/bin/bash

echo "========================================"
echo " 자율주행 비디오 분석 시스템"
echo "========================================"
echo

# 가상환경 활성화
if [ -f "gpu_venv/bin/activate" ]; then
    source gpu_venv/bin/activate
    echo "[OK] 가상환경 활성화 완료"
else
    echo "[주의] 가상환경을 찾을 수 없습니다"
fi

echo
echo "비디오 분석 시작..."
echo

# 인자 그대로 전달
python run.py "$@"
"""

# ============================================================================
# 사용 예제 모음
# ============================================================================

"""
# 1. 기본 실행 (screen_1766557465783.mp4 사용)
python run.py

# 2. 비디오 파일만 지정 (가장 간단)
python run.py screen_1766557465783.mp4
python run.py C:/Videos/test.mp4
python run.py screen_1766557465783.mp4

# 3. 명시적 플래그 사용
python run.py --video my_video.mp4

# 4. GPU 없이 실행
python run.py --no-gpu
python run.py my_video.mp4 --no-gpu
python run.py --video my_video.mp4 --no-gpu

# 5. 배치 파일 사용 (Windows)
quick_start.bat
quick_start.bat my_video.mp4
quick_start.bat my_video.mp4 --no-gpu

# 6. 도움말 보기
python run.py --help
python run.py -h
"""