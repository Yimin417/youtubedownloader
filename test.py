"""
Test script to verify the YouTube downloader core functionality
"""
import sys
import io
from pathlib import Path

# Ensure UTF-8 encoding for output
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=" * 60)
print("YouTube Downloader - Verification Test")
print("=" * 60)

errors = []

# Test 1: Import all modules
print("\n[Test 1] Importing modules...")
try:
    from downloader.engine import DownloadEngine, VideoInfo, DownloadStatus
    print("  [OK] downloader.engine")
    from downloader.formats import FormatManager
    print("  [OK] downloader.formats")
    from utils.config import ConfigManager, AppConfig
    print("  [OK] utils.config")
    from utils.logger import Logger
    print("  [OK] utils.logger")
    from downloader.progress import ProgressTracker, DownloadHistory, DownloadItem, ProgressState
    print("  [OK] downloader.progress")
    from gui.theme import setup_theme, get_theme_colors, FONT_CONFIG, SPACING
    print("  [OK] gui.theme")
except ImportError as e:
    errors.append(f"Import error: {e}")
    print(f"  [FAIL] Import error: {e}")

# Test 2: Config Manager
if not errors:
    print("\n[Test 2] ConfigManager...")
    try:
        test_config = AppConfig()
        print(f"  [OK] Default config: {test_config.default_download_path}")
        print(f"      resolution={test_config.default_resolution}, format={test_config.default_format}")
    except Exception as e:
        errors.append(f"Config error: {e}")
        print(f"  [FAIL] {e}")

# Test 3: Download Engine
if not errors:
    print("\n[Test 3] DownloadEngine...")
    try:
        engine = DownloadEngine()
        print(f"  [OK] Engine init, {len(engine.SUPPORTED_RESOLUTIONS)} resolutions")
    except Exception as e:
        errors.append(f"Engine error: {e}")
        print(f"  [FAIL] {e}")

# Test 4: Format Manager
if not errors:
    print("\n[Test 4] FormatManager...")
    try:
        video = FormatManager.get_video_formats()
        audio = FormatManager.get_audio_formats()
        res = FormatManager.get_resolution_options()
        print(f"  [OK] Video: {len(video)}, Audio: {len(audio)}, Res: {len(res)}")
    except Exception as e:
        errors.append(f"Format error: {e}")
        print(f"  [FAIL] {e}")

# Test 5: Progress
if not errors:
    print("\n[Test 5] ProgressTracker/History...")
    try:
        tracker = ProgressTracker()
        history = DownloadHistory()
        print(f"  [OK] Tracker state={tracker.state.value}, History max={history.MAX_HISTORY}")
    except Exception as e:
        errors.append(f"Progress error: {e}")
        print(f"  [FAIL] {e}")

# Test 6: Theme
if not errors:
    print("\n[Test 6] Theme configuration...")
    try:
        dark = get_theme_colors('dark')
        light = get_theme_colors('light')
        print(f"  [OK] Dark: {len(dark)} colors, Light: {len(light)}")
        print(f"      Fonts: {len(FONT_CONFIG)}, Spacing: {len(SPACING)}")
    except Exception as e:
        errors.append(f"Theme error: {e}")
        print(f"  [FAIL] {e}")

print("\n" + "=" * 60)
if not errors:
    print("SUCCESS - All basic tests passed!")
else:
    print(f"FAILED - {len(errors)} test(s) failed")
    for err in errors:
        print(f"  - {err}")
print("=" * 60)
print("\nNext steps:")
print("  1. All dependencies installed in venv")
print("  2. GUI created at src/gui/main.py")
print("  3. Run: python main.py (or venv\\Scripts\\python main.py)")
print("=" * 60)
