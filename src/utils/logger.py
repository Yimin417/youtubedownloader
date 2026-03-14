"""
Logging utilities for the downloader application
"""
import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime


class Logger:
    """Application logger with file and console output"""

    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        name: str = "youtube-downloader",
        log_level: int = logging.INFO,
        log_dir: Optional[str] = None,
        console_output: bool = True
    ):
        """
        Initialize logger

        Args:
            name: Logger name
            log_level: Logging level
            log_dir: Directory for log files
            console_output: Whether to output to console
        """
        if self._logger is not None:
            return  # Already initialized

        self._logger = logging.getLogger(name)
        self._logger.setLevel(log_level)

        # Clear existing handlers
        self._logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # File handler
        if log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)

            # Log file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_path / f"downloader_{timestamp}.log"

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

            # Also create a symlink to "latest.log" for easy access
            latest_log = log_path / "latest.log"
            if latest_log.exists() or latest_log.is_symlink():
                latest_log.unlink()
            try:
                latest_log.symlink_to(log_file)
            except (OSError, NotImplementedError):
                # Symlinks not supported on all systems
                pass

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the underlying logger instance"""
        if cls._instance is None:
            cls()
        return cls._logger

    def debug(self, msg: str):
        self._logger.debug(msg)

    def info(self, msg: str):
        self._logger.info(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def critical(self, msg: str):
        self._logger.critical(msg)

    def exception(self, msg: str):
        self._logger.exception(msg)

    def set_level(self, level: int):
        """Change logging level"""
        if self._logger:
            self._logger.setLevel(level)


# Convenience functions
def get_logger() -> logging.Logger:
    """Get the application logger"""
    return Logger.get_logger()


def log_debug(msg: str):
    get_logger().debug(msg)


def log_info(msg: str):
    get_logger().info(msg)


def log_warning(msg: str):
    get_logger().warning(msg)


def log_error(msg: str):
    get_logger().error(msg)


def log_exception(msg: str):
    get_logger().exception(msg)
