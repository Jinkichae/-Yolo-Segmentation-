# ============================================================================
# src/main.py
# 애플리케이션 진입점
# ============================================================================
# ============================================================================
# src/main.py
# 애플리케이션 진입점 (직접 실행 가능)
# ============================================================================

import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

# 이제 절대 import 사용
from src.ui.main_window import MainWindow
from src.config.constants import APP_CONST


def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description=f'{APP_CONST.APP_NAME} v{APP_CONST.APP_VERSION}'
    )
    parser.add_argument(
        '--video',
        type=str,
        default=APP_CONST.DEFAULT_VIDEO_FILE,
        help='비디오 파일 경로'
    )
    parser.add_argument(
        '--no-gpu',
        action='store_true',
        help='GPU 사용 안함'
    )
    return parser.parse_args()


def main():
    """메인 함수"""
    args = parse_arguments()

    # 설정 적용
    from src.config.settings import SettingsManager
    settings = SettingsManager()

    if args.no_gpu:
        settings.set('use_gpu', False)

    # Qt 애플리케이션
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_CONST.APP_NAME)
    app.setApplicationVersion(APP_CONST.APP_VERSION)

    # 메인 윈도우
    window = MainWindow(video_path=args.video)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

'''
cd E:\[tinda]\[ClaudeAI]\2025_1224_yolo\-Yolo-Segmentation-
E:\[HuhBible]\gpu_venv\Scripts\activate.bat
main.py

'''