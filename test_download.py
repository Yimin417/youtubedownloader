#!/usr/bin/env python3
"""Simple test to verify download functionality"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from downloader.engine import DownloadEngine

def test_download():
    print("Creating engine...")
    engine = DownloadEngine()

    # Set a progress callback
    def progress_callback(progress):
        print(f"[PROGRESS] {progress.status.value}: {progress.progress:.1f}% - {progress.speed} - {progress.eta}")

    engine.set_progress_callback(progress_callback)

    print("Starting download...")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 经典测试视频

    try:
        success = engine.download(
            url=url,
            resolution="360",  # 低分辨率快速测试
            output_format="mp4",
            download_subtitles=False,
            embed_subtitle=False,
            download_thumbnail=False
        )
        print(f"[RESULT] Download {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download()
