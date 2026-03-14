"""
Format handling utilities for video/audio conversion
"""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class FormatOption:
    """Represents a format option for download"""
    format_id: str
    name: str
    extension: str
    quality: str
    description: str


class FormatManager:
    """Manage video/audio format options"""

    VIDEO_FORMATS = [
        FormatOption("mp4", "MP4", "mp4", "high", "Most compatible format"),
        FormatOption("webm", "WebM", "webm", "high", "Open source format"),
        FormatOption("mkv", "MKV", "mkv", "high", "Matroska container"),
    ]

    AUDIO_FORMATS = [
        FormatOption("mp3", "MP3", "mp3", "320kbps", "Most compatible audio"),
        FormatOption("m4a", "M4A", "m4a", "256kbps", "Apple audio format"),
        FormatOption("wav", "WAV", "wav", "lossless", "Uncompressed audio"),
        FormatOption("flac", "FLAC", "flac", "lossless", "Lossless compression"),
    ]

    RESOLUTION_LABELS = {
        "8192": "8K",
        "4320": "4K",
        "2160": "2160p",
        "1440": "1440p",
        "1080": "1080p",
        "720": "720p",
        "480": "480p",
        "360": "360p",
        "240": "240p",
        "144": "144p",
    }

    @classmethod
    def get_video_formats(cls) -> List[FormatOption]:
        """Get available video formats"""
        return cls.VIDEO_FORMATS.copy()

    @classmethod
    def get_audio_formats(cls) -> List[FormatOption]:
        """Get available audio formats"""
        return cls.AUDIO_FORMATS.copy()

    @classmethod
    def get_resolution_label(cls, height: str) -> str:
        """Get display label for resolution height"""
        return cls.RESOLUTION_LABELS.get(height, f"{height}p")

    @classmethod
    def get_resolution_options(cls) -> List[tuple]:
        """Get all resolution options for UI"""
        return [
            (height, label) for height, label in cls.RESOLUTION_LABELS.items()
        ]

    @classmethod
    def filter_formats_by_resolution(
        cls,
        formats: List[Dict],
        max_resolution: str = "1080"
    ) -> List[Dict]:
        """Filter formats by maximum resolution"""
        max_height = int(max_resolution)
        return [f for f in formats if f.get('height', 0) <= max_height]

    @classmethod
    def get_best_format(
        cls,
        formats: List[Dict],
        preferred_resolution: str = "1080"
    ) -> Optional[Dict]:
        """Get best matching format for preferred resolution"""
        preferred_height = int(preferred_resolution)

        # Find formats at or below preferred resolution
        matching = [f for f in formats if f.get('height', 0) <= preferred_height]

        if not matching:
            return None

        # Return the highest quality matching format
        return max(matching, key=lambda x: x.get('height', 0))

    @classmethod
    def parse_resolution(cls, resolution_str: str) -> int:
        """Parse resolution string to height integer"""
        try:
            return int(resolution_str)
        except ValueError:
            return 1080  # Default to 1080p

    @classmethod
    def get_subtitle_languages(cls) -> List[tuple]:
        """Get common subtitle language options"""
        return [
            ("en", "English"),
            ("es", "Spanish"),
            ("fr", "French"),
            ("de", "German"),
            ("it", "Italian"),
            ("pt", "Portuguese"),
            ("ru", "Russian"),
            ("ja", "Japanese"),
            ("ko", "Korean"),
            ("zh", "Chinese (Simplified)"),
            ("zh-TW", "Chinese (Traditional)"),
            ("ar", "Arabic"),
            ("hi", "Hindi"),
        ]
