# ============================================================================
# verify.py
# 프로젝트 루트에 생성하여 설치 확인
# ============================================================================

"""
자율주행 비디오 분석 시스템 - 설치 검증 스크립트

사용법:
    python verify.py
"""

import sys
from pathlib import Path

# 프로젝트 루트 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_header(text):
    """헤더 출력"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step, text):
    """단계 출력"""
    print(f"\n[{step}] {text}")


def print_success(text):
    """성공 메시지"""
    print(f"  ✓ {text}")


def print_error(text):
    """오류 메시지"""
    print(f"  ✗ {text}")


def check_python_packages():
    """필수 패키지 확인"""
    print_step("1/4", "필수 패키지 확인")

    packages = {
        'PySide6': 'PySide6',
        'numpy': 'numpy',
        'cv2': 'opencv-python',
        'ultralytics': 'ultralytics',
        'torch': 'torch',
    }

    all_ok = True
    for module, package in packages.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print_success(f"{package}: {version}")
        except ImportError:
            print_error(f"{package} not installed")
            all_ok = False

    return all_ok


def check_cuda():
    """CUDA 확인"""
    print_step("2/4", "GPU/CUDA 확인")

    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print_success(f"CUDA 사용 가능")
            print_success(f"CUDA 버전: {torch.version.cuda}")
            print_success(f"GPU 개수: {torch.cuda.device_count()}")
            if torch.cuda.device_count() > 0:
                print_success(f"GPU 이름: {torch.cuda.get_device_name(0)}")
        else:
            print_error("CUDA 사용 불가 (CPU 모드로 실행됩니다)")

        return True
    except Exception as e:
        print_error(f"CUDA 확인 실패: {e}")
        return False


def check_project_structure():
    """프로젝트 구조 확인"""
    print_step("3/4", "프로젝트 구조 확인")

    required_dirs = [
        'src',
        'src/config',
        'src/core',
        'src/models',
        'src/ui',
        'src/ui/widgets',
        'src/ui/styles',
        'src/utils',
    ]

    all_ok = True
    for dir_path in required_dirs:
        path = PROJECT_ROOT / dir_path
        if path.exists():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ 없음")
            all_ok = False

    return all_ok


def check_imports():
    """모듈 Import 확인"""
    print_step("4/4", "모듈 Import 확인")

    modules = [
        ('src.config.constants', 'APP_CONST, COLOR'),
        ('src.config.settings', 'SettingsManager'),
        ('src.models.stats', 'DetectionStats'),
        ('src.models.detection', 'Detection, LaneLines'),
        ('src.utils.geometry', 'GeometryUtils'),
        ('src.utils.drawing', 'DrawingUtils'),
        ('src.utils.performance', 'PerformanceMonitor'),
        ('src.core.model_manager', 'ModelManager'),
        ('src.core.lane_detector', 'LaneDetector'),
        ('src.core.detection_engine', 'DetectionEngine'),
        ('src.core.video_processor', 'VideoProcessor'),
        ('src.ui.widgets.progress_bar', 'MediaProgressBar'),
        ('src.ui.widgets.stats_widget', 'StatsWidget'),
        ('src.ui.main_window', 'MainWindow'),
    ]

    all_ok = True
    for module_path, items in modules:
        try:
            __import__(module_path)
            print_success(f"{module_path}")
        except Exception as e:
            print_error(f"{module_path}: {str(e)[:50]}")
            all_ok = False

    return all_ok


def check_video_file():
    """기본 비디오 파일 확인"""
    print("\n" + "-" * 60)
    print("기본 비디오 파일 확인")
    print("-" * 60)

    video_file = PROJECT_ROOT / "screen_1766557465783.mp4"
    if video_file.exists():
        size_mb = video_file.stat().st_size / (1024 * 1024)
        print_success(f"기본 비디오 파일 존재: {size_mb:.2f} MB")
    else:
        print_error("기본 비디오 파일 없음 (다른 비디오를 사용하세요)")


def test_settings():
    """설정 관리자 테스트"""
    print("\n" + "-" * 60)
    print("설정 관리자 테스트")
    print("-" * 60)

    try:
        from src.config.settings import SettingsManager
        settings = SettingsManager()

        print_success("SettingsManager 생성 완료")
        print_success(f"기본 설정: {list(settings.to_dict().keys())}")

        # 설정 변경 테스트
        settings.set('confidence_threshold', 0.7)
        value = settings.get('confidence_threshold')
        assert value == 0.7, "설정값 불일치"
        print_success("설정 변경 테스트 통과")

        return True
    except Exception as e:
        print_error(f"설정 테스트 실패: {e}")
        return False


def test_model_manager():
    """모델 관리자 테스트"""
    print("\n" + "-" * 60)
    print("모델 관리자 테스트")
    print("-" * 60)

    try:
        from src.core.model_manager import ModelManager
        manager = ModelManager()

        print_success("ModelManager 생성 완료")
        print_success(f"Device: {manager.device}")
        print_success(f"Detection model: {manager.detection_model_name}")
        print_success(f"Segmentation model: {manager.segmentation_model_name}")

        return True
    except Exception as e:
        print_error(f"모델 관리자 테스트 실패: {e}")
        return False


def main():
    """메인 함수"""
    print_header("🚗 자율주행 비디오 분석 시스템 - 설치 검증")

    results = []

    # 1. 패키지 확인
    results.append(("패키지", check_python_packages()))

    # 2. CUDA 확인
    results.append(("CUDA", check_cuda()))

    # 3. 프로젝트 구조
    results.append(("프로젝트 구조", check_project_structure()))

    # 4. Import 확인
    results.append(("모듈 Import", check_imports()))

    # 5. 추가 테스트
    check_video_file()
    results.append(("설정 관리자", test_settings()))
    results.append(("모델 관리자", test_model_manager()))

    # 결과 요약
    print_header("검증 결과 요약")

    for name, success in results:
        status = "✓ 통과" if success else "✗ 실패"
        print(f"  {name:20s} : {status}")

    all_passed = all(success for _, success in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("  ✅ 모든 검증 통과! 프로그램을 실행할 수 있습니다.")
        print("\n  실행 방법:")
        print("    python run.py")
        print("    python run.py screen_1766557465783.mp4")
        print("    python run.py --video your_video.mp4")
    else:
        print("  ⚠️  일부 검증 실패. 위의 오류를 확인하세요.")
        print("\n  해결 방법:")
        print("    pip install PySide6 numpy opencv-python ultralytics torch")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())