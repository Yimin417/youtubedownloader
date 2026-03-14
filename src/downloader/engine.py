"""
YouTube Download Engine - yt-dlp wrapper with progress tracking
"""
import yt_dlp
import threading
import os
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class VideoInfo:
    """Video metadata"""
    id: str
    title: str
    duration: int  # seconds
    thumbnail: str
    uploader: str
    view_count: int
    description: str
    is_playlist: bool = False
    playlist_count: int = 0
    available_formats: List[Dict] = None
    available_subtitles: List[str] = None


@dataclass
class DownloadProgress:
    """Download progress information"""
    status: DownloadStatus
    progress: float  # 0-100
    speed: str  # e.g., "1.5 MiB/s"
    eta: str  # e.g., "00:30"
    downloaded: str  # e.g., "10.5 MiB"
    total: str  # e.g., "50.0 MiB"
    filename: str
    error: Optional[str] = None


class DownloadEngine:
    """Core download engine using yt-dlp"""

    SUPPORTED_RESOLUTIONS = [
        ("8192", "8K"),
        ("4320", "4K"),
        ("2160", "2160p"),
        ("1440", "1440p"),
        ("1080", "1080p"),
        ("720", "720p"),
        ("480", "480p"),
        ("360", "360p"),
        ("240", "240p"),
        ("144", "144p"),
    ]

    def __init__(self, download_path: str = ".", logger=None):
        self.download_path = download_path
        self.logger = logger
        self._current_download: Optional[str] = None
        self._cancel_flag = False
        self._progress_callback: Optional[Callable[[DownloadProgress], None]] = None

    def set_progress_callback(self, callback: Callable[[DownloadProgress], None]):
        """Set callback for progress updates"""
        self._progress_callback = callback

    def set_download_path(self, path: str):
        """Set the download directory path"""
        self.download_path = path
        os.makedirs(path, exist_ok=True)

    def get_video_info(self, url: str, fast_mode: bool = True) -> VideoInfo:
        """Fetch video information without downloading

        Args:
            url: Video URL
            fast_mode: If True, only fetch basic info (no format list, no subtitles)
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': fast_mode,  # Fast mode: just basic metadata
            'socket_timeout': 10,
            'retries': 2,
            'fragment_retries': 2,
            'skip_unavailable_fragments': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            raise Exception(f"Failed to fetch video info: {str(e)}")

            # Handle playlist
            is_playlist = info.get('_type') == 'playlist'

            if is_playlist:
                entries = list(info.get('entries', []))
                playlist_count = len(entries)
                # Get info from first video in playlist for display
                first_video = entries[0] if entries else {}
                title = info.get('title', f'Playlist ({playlist_count} videos)')
                video_id = info.get('id', '')
                duration = first_video.get('duration', 0)
                thumbnail = first_video.get('thumbnail', '')
                uploader = first_video.get('uploader', 'Various')
                view_count = first_video.get('view_count', 0)
                description = info.get('description', '')
            else:
                title = info.get('title', 'Unknown')
                video_id = info.get('id', '')
                duration = info.get('duration', 0)
                thumbnail = info.get('thumbnail', '')
                uploader = info.get('uploader', 'Unknown')
                view_count = info.get('view_count', 0)
                description = info.get('description', '')
                playlist_count = 0

            # Extract available formats
            available_formats = self._extract_formats(info)

            # Extract available subtitles
            available_subtitles = list(info.get('subtitles', {}).keys())

            return VideoInfo(
                id=video_id,
                title=title,
                duration=duration,
                thumbnail=thumbnail,
                uploader=uploader,
                view_count=view_count,
                description=description,
                is_playlist=is_playlist,
                playlist_count=playlist_count,
                available_formats=available_formats,
                available_subtitles=available_subtitles
            )

    def _extract_formats(self, info: Dict) -> List[Dict]:
        """Extract and organize available formats"""
        formats = info.get('formats', [])
        quality_map = {}

        for fmt in formats:
            # Skip audio-only formats for video download
            if fmt.get('vcodec') == 'none':
                continue

            height = fmt.get('height')
            if not height:
                continue

            # Get the best format for each resolution
            if height not in quality_map or fmt.get('fps', 0) > quality_map[height].get('fps', 0):
                quality_map[height] = fmt

        result = []
        for height, fmt in sorted(quality_map.items(), reverse=True):
            result.append({
                'format_id': fmt.get('format_id', ''),
                'height': height,
                'resolution': f"{height}p",
                'fps': fmt.get('fps', 30),
                'ext': fmt.get('ext', 'mp4'),
                'filesize': fmt.get('filesize'),
                'quality': fmt.get('quality', 0)
            })

        return result

    def _progress_hook(self, d: Dict):
        """yt-dlp progress hook"""
        print(f"[ENGINE DEBUG] Progress hook called: {d.get('status')}, callback exists: {self._progress_callback is not None}")
        import sys
        sys.stdout.flush()

        if not self._progress_callback:
            print("[ENGINE DEBUG] No callback, returning")
            return

        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)

            if total > 0:
                progress = (downloaded / total) * 100
            else:
                progress = 0

            self._progress_callback(DownloadProgress(
                status=DownloadStatus.DOWNLOADING,
                progress=progress,
                speed=d.get('speed_str', 'N/A'),
                eta=d.get('eta_str', 'N/A'),
                downloaded=d.get('_percent_str', '0%'),
                total=d.get('total_bytes_str', 'N/A'),
                filename=d.get('filename', '')
            ))

        elif d['status'] == 'finished':
            self._progress_callback(DownloadProgress(
                status=DownloadStatus.COMPLETED,
                progress=100,
                speed='',
                eta='',
                downloaded='100%',
                total='',
                filename=d.get('filename', '')
            ))

        elif d['status'] == 'error':
            self._progress_callback(DownloadProgress(
                status=DownloadStatus.ERROR,
                progress=0,
                speed='',
                eta='',
                downloaded='',
                total='',
                filename='',
                error=d.get('error', 'Unknown error')
            ))

    def download(
        self,
        url: str,
        resolution: str = "1080",
        output_format: str = "mp4",
        output_path: Optional[str] = None,
        download_subtitles: bool = False,
        subtitle_langs: Optional[List[str]] = None,
        embed_subtitle: bool = False,
        download_thumbnail: bool = False,
        playlist_start: int = 1,
        playlist_end: Optional[int] = None
    ) -> bool:
        """
        Download video with specified options

        Args:
            url: Video or playlist URL
            resolution: Target resolution height (e.g., "1080", "720")
            output_format: Output format (mp4, webm, mp3)
            output_path: Custom output path
            download_subtitles: Whether to download subtitles
            subtitle_langs: List of subtitle languages to download
            embed_subtitle: Whether to embed subtitles in video
            download_thumbnail: Whether to download thumbnail
            playlist_start: Playlist start index (1-based)
            playlist_end: Playlist end index (None for all)

        Returns:
            True if successful, False otherwise
        """
        self._cancel_flag = False
        self._current_download = url
        output_path = output_path or self.download_path
        os.makedirs(output_path, exist_ok=True)

        # Build format selector - simple and reliable
        if output_format == "mp3":
            # Audio only
            format_selector = "bestaudio/best"
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            # Video + audio - use format that doesn't require FFmpeg merging if possible
            # Try to get best combined format first (faster, no FFmpeg needed)
            format_selector = f"best[height<={resolution}]/best"
            postprocessors = []

        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': False,
            'no_warnings': True,
            'ignoreerrors': False,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            # Handle filenames with special chars
            'restrictfilenames': False,
            'windowsfilenames': False,
        }

        # Subtitle options (only if requested)
        if download_subtitles and subtitle_langs:
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = subtitle_langs
            if embed_subtitle:
                ydl_opts['embedsubtitles'] = True

        # Thumbnail options (disabled by default)
        if download_thumbnail:
            ydl_opts['writethumbnail'] = True

        # Playlist options
        if playlist_start > 1:
            ydl_opts['playliststart'] = playlist_start
        if playlist_end:
            ydl_opts['playlistend'] = playlist_end

        # Cancellation check
        def check_cancel():
            if self._cancel_flag:
                raise Exception("Download cancelled by user")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.add_progress_hook(lambda d: check_cancel())
                # This is the actual download call
                ydl.download([url])
            return True
        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.error(f"Download error: {error_msg}")
            if self._progress_callback:
                self._progress_callback(DownloadProgress(
                    status=DownloadStatus.ERROR,
                    progress=0,
                    speed='',
                    eta='',
                    downloaded='',
                    total='',
                    filename='',
                    error=error_msg
                ))
            return False

    def cancel(self):
        """Cancel current download"""
        self._cancel_flag = True

    def is_downloading(self) -> bool:
        """Check if currently downloading"""
        return self._current_download is not None and not self._cancel_flag

    def get_supported_resolutions(self) -> List[tuple]:
        """Get list of supported resolutions"""
        return self.SUPPORTED_RESOLUTIONS.copy()
