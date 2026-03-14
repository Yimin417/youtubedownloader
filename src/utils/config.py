"""
Configuration management for the downloader application
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class AppConfig:
    """Application configuration"""
    # Download settings
    default_download_path: str = field(default_factory=lambda: str(Path.home() / "Downloads" / "YouTube"))
    default_resolution: str = "1080"
    default_format: str = "mp4"

    # Subtitle settings
    download_subtitles: bool = False
    subtitle_languages: list = field(default_factory=lambda: ["en"])
    embed_subtitles: bool = False

    # Thumbnail settings
    download_thumbnail: bool = True

    # Playlist settings
    playlist_download_all: bool = True

    # UI settings
    theme: str = "dark"  # "dark" or "light"
    language: str = "en"

    # Advanced settings
    max_concurrent_downloads: int = 1
    auto_exit: bool = False

    # History settings
    keep_history: bool = True
    history_limit: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create from dictionary"""
        # Filter out unknown keys
        valid_keys = set(f.name for f in cls.__dataclass_fields__.values())
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


class ConfigManager:
    """Manage application configuration persistence"""

    CONFIG_FILE = "config.json"

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config manager

        Args:
            config_dir: Directory to store config file.
                       Uses app directory if not specified.
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use app directory (same directory as main.py)
            self.config_dir = Path(__file__).parent.parent.parent
        self.config_path = self.config_dir / self.CONFIG_FILE
        self._config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        """Load configuration from file"""
        if not self.config_path.exists():
            # Create default config
            self._config = AppConfig()
            self.save()
            return self._config

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._config = AppConfig.from_dict(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading config: {e}. Using defaults.")
            self._config = AppConfig()

        return self._config

    def save(self, config: Optional[AppConfig] = None):
        """Save configuration to file"""
        if config:
            self._config = config

        if not self._config:
            return

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self) -> AppConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load()
        return self._config

    def update(self, **kwargs):
        """Update configuration values"""
        config = self.get()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save()

    def reset(self):
        """Reset to default configuration"""
        self._config = AppConfig()
        self.save()

    def delete(self):
        """Delete configuration file"""
        if self.config_path.exists():
            self.config_path.unlink()
        self._config = None


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """Get or create global config manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)
    return _config_manager


def get_config() -> AppConfig:
    """Get current application configuration"""
    return get_config_manager().get()


def save_config(config: Optional[AppConfig] = None):
    """Save application configuration"""
    get_config_manager().save(config)
