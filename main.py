#!/usr/bin/env python3
"""
YouTube Video Downloader - Main Entry Point

A modern GUI application for downloading videos from YouTube
with support for multiple formats, resolutions, and playlists.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Also add current directory for package imports
current_dir = str(Path(__file__).parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import gui.main

if __name__ == "__main__":
    gui.main.main()
