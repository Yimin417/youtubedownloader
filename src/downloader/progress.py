"""
Download progress tracking and history
"""
import threading
import time
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProgressState(Enum):
    IDLE = "idle"
    FETCHING = "fetching"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class DownloadItem:
    """Represents a download item in history"""
    url: str
    title: str
    status: ProgressState
    progress: float
    speed: str
    eta: str
    filename: str
    output_path: str
    resolution: str
    format: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    file_size: int = 0
    error_message: Optional[str] = None
    thumbnail: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'url': self.url,
            'title': self.title,
            'status': self.status.value,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'filename': self.filename,
            'output_path': self.output_path,
            'resolution': self.resolution,
            'format': self.format,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_size': self.file_size,
            'error_message': self.error_message,
            'thumbnail': self.thumbnail,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DownloadItem':
        """Create from dictionary"""
        return cls(
            url=data['url'],
            title=data['title'],
            status=ProgressState(data['status']),
            progress=data['progress'],
            speed=data['speed'],
            eta=data['eta'],
            filename=data['filename'],
            output_path=data['output_path'],
            resolution=data['resolution'],
            format=data['format'],
            started_at=datetime.fromisoformat(data['started_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            file_size=data.get('file_size', 0),
            error_message=data.get('error_message'),
            thumbnail=data.get('thumbnail'),
        )


class ProgressTracker:
    """Track download progress with observer pattern"""

    def __init__(self):
        self._state = ProgressState.IDLE
        self._progress = 0.0
        self._speed = "N/A"
        self._eta = "N/A"
        self._filename = ""
        self._current_url: Optional[str] = None
        self._lock = threading.Lock()
        self._observers: List[Callable[['ProgressTracker'], None]] = []

    @property
    def state(self) -> ProgressState:
        with self._lock:
            return self._state

    @state.setter
    def state(self, value: ProgressState):
        with self._lock:
            self._state = value
            self._notify_observers()

    @property
    def progress(self) -> float:
        with self._lock:
            return self._progress

    @progress.setter
    def progress(self, value: float):
        with self._lock:
            self._progress = max(0.0, min(100.0, value))
            self._notify_observers()

    @property
    def speed(self) -> str:
        with self._lock:
            return self._speed

    @speed.setter
    def speed(self, value: str):
        with self._lock:
            self._speed = value
            self._notify_observers()

    @property
    def eta(self) -> str:
        with self._lock:
            return self._eta

    @eta.setter
    def eta(self, value: str):
        with self._lock:
            self._eta = value
            self._notify_observers()

    @property
    def filename(self) -> str:
        with self._lock:
            return self._filename

    @filename.setter
    def filename(self, value: str):
        with self._lock:
            self._filename = value
            self._notify_observers()

    @property
    def current_url(self) -> Optional[str]:
        with self._lock:
            return self._current_url

    @current_url.setter
    def current_url(self, value: str):
        with self._lock:
            self._current_url = value
            self._notify_observers()

    def add_observer(self, callback: Callable[['ProgressTracker'], None]):
        """Add an observer to be notified of progress changes"""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable[['ProgressTracker'], None]):
        """Remove an observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notify all observers of state change"""
        for observer in self._observers:
            try:
                observer(self)
            except Exception:
                pass  # Don't let observer errors break the download

    def reset(self):
        """Reset tracker to initial state"""
        with self._lock:
            self._state = ProgressState.IDLE
            self._progress = 0.0
            self._speed = "N/A"
            self._eta = "N/A"
            self._filename = ""
            self._current_url = None
            self._notify_observers()

    def get_status_text(self) -> str:
        """Get human-readable status text"""
        with self._lock:
            if self._state == ProgressState.FETCHING:
                return "Fetching video info..."
            elif self._state == ProgressState.DOWNLOADING:
                return f"Downloading: {self._progress:.1f}% ({self._speed})"
            elif self._state == ProgressState.COMPLETED:
                return "Download complete!"
            elif self._state == ProgressState.ERROR:
                return "Download failed!"
            elif self._state == ProgressState.CANCELLED:
                return "Download cancelled"
            else:
                return "Ready"


class DownloadHistory:
    """Maintain history of downloads"""

    MAX_HISTORY = 10

    def __init__(self):
        self._items: List[DownloadItem] = []
        self._lock = threading.Lock()

    def add(self, item: DownloadItem):
        """Add item to history"""
        with self._lock:
            # Remove existing entry with same URL if present
            self._items = [i for i in self._items if i.url != item.url]
            # Add to front
            self._items.insert(0, item)
            # Trim to max size
            self._items = self._items[:self.MAX_HISTORY]

    def remove(self, url: str):
        """Remove item from history"""
        with self._lock:
            self._items = [i for i in self._items if i.url != url]

    def clear(self):
        """Clear all history"""
        with self._lock:
            self._items.clear()

    def get_all(self) -> List[DownloadItem]:
        """Get all history items"""
        with self._lock:
            return self._items.copy()

    def get_recent(self, count: int = 5) -> List[DownloadItem]:
        """Get most recent history items"""
        with self._lock:
            return self._items[:count]

    def get_failed(self) -> List[DownloadItem]:
        """Get failed downloads"""
        with self._lock:
            return [i for i in self._items if i.status in (ProgressState.ERROR, ProgressState.CANCELLED)]

    def get_completed(self) -> List[DownloadItem]:
        """Get completed downloads"""
        with self._lock:
            return [i for i in self._items if i.status == ProgressState.COMPLETED]

    def to_list(self) -> List[Dict]:
        """Convert to list of dictionaries"""
        with self._lock:
            return [item.to_dict() for item in self._items]

    @classmethod
    def from_list(cls, items: List[Dict]) -> 'DownloadHistory':
        """Create from list of dictionaries"""
        history = cls()
        for item_data in items:
            try:
                history.add(DownloadItem.from_dict(item_data))
            except Exception:
                continue  # Skip invalid entries
        return history
