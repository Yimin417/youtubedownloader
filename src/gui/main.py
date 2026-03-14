"""
Main GUI Application for YouTube Downloader
"""
import os
import sys
import threading
import io
import time
import customtkinter as ctk
from typing import Optional, List, Tuple
from datetime import datetime
from pathlib import Path

# Add parent directory to path for package imports
current_dir = Path(__file__).parent.parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from downloader.engine import DownloadEngine, VideoInfo, DownloadStatus
from downloader.formats import FormatManager
from downloader.progress import ProgressTracker, DownloadHistory, ProgressState, DownloadItem
from utils.config import ConfigManager, get_config, save_config
from utils.logger import Logger
from gui.theme import setup_theme, get_theme_colors, FONT_CONFIG, SPACING, CORNER_RADIUS


class MainApplication(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Configuration
        self.config = get_config()
        self.config_manager = ConfigManager()

        # Initialize components
        self.engine = DownloadEngine(self.config.default_download_path)
        self.tracker = ProgressTracker()
        self.history = DownloadHistory()
        self.format_manager = FormatManager()
        self.logger = Logger()

        # State
        self.is_downloading = False
        self._active_thread: Optional[threading.Thread] = None

        # Setup UI
        self._setup_window()
        self._setup_theme()
        self._create_widgets()
        self._bind_events()
        self._load_history()

    def _setup_window(self):
        """Configure main window"""
        self.title("YouTube Downloader")
        self.geometry("900x650")
        self.minsize(800, 600)

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 900) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"+{x}+{y}")

    def _setup_theme(self):
        """Apply theme settings"""
        setup_theme(self.config.theme)
        colors = get_theme_colors(self.config.theme)
        self.configure(fg_color=colors["fg_color"])

    def _create_widgets(self):
        """Create all UI widgets"""
        colors = get_theme_colors(self.config.theme)

        # Main container with padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Header
        self._create_header()

        # URL Input Section
        self._create_url_section()

        # Options Frame
        self._create_options_frame()

        # Progress Section
        self._create_progress_section()

        # Video Info Section
        self._create_video_info_section()

        # Buttons Section
        self._create_buttons_section()

        # History Section
        self._create_history_section()

    def _create_header(self):
        """Create header with title and theme toggle"""
        header = ctk.CTkFrame(self.main_container, height=60)
        header.pack(fill="x", pady=(0, SPACING["lg"]))
        header.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header,
            text="🎬 YouTube Downloader",
            font=FONT_CONFIG["title"]
        )
        title_label.pack(side="left", padx=SPACING["lg"], pady=SPACING["md"])

        # Theme toggle
        self.theme_var = ctk.StringVar(value=self.config.theme)
        theme_menu = ctk.CTkOptionMenu(
            header,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._on_theme_change,
            width=100,
            font=FONT_CONFIG["body"]
        )
        theme_menu.pack(side="right", padx=SPACING["lg"], pady=SPACING["md"])

        # Settings button
        settings_btn = ctk.CTkButton(
            header,
            text="⚙️ Settings",
            width=100,
            command=self._open_settings,
            font=FONT_CONFIG["body"]
        )
        settings_btn.pack(side="right", padx=(0, SPACING["md"]), pady=SPACING["md"])

    def _create_url_section(self):
        """Create URL input section with Download button"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        # Title
        url_label = ctk.CTkLabel(
            frame,
            text="Video URL:",
            font=FONT_CONFIG["heading"]
        )
        url_label.pack(anchor="w", padx=SPACING["md"], pady=SPACING["md"])

        # URL Entry and Download button in same row
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        self.url_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Enter YouTube URL here...",
            font=FONT_CONFIG["body"],
            height=45
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))

        # BIG Download button right next to input
        self.download_btn = ctk.CTkButton(
            entry_frame,
            text="⬇️ DOWNLOAD",
            width=150,
            height=45,
            command=self._start_download,
            font=("Helvetica", 14, "bold"),
            fg_color="#388e3c",
            hover_color="#2e7d32"
        )
        self.download_btn.pack(side="right")
        # Debug: bind click event
        self.download_btn.bind("<Button-1>", lambda e: print("[DEBUG] Download button clicked!"))

    def _create_options_frame(self):
        """Create download options frame"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        # Title
        options_label = ctk.CTkLabel(
            frame,
            text="Download Options",
            font=FONT_CONFIG["heading"]
        )
        options_label.pack(anchor="w", padx=SPACING["md"], pady=SPACING["md"])

        # Options grid
        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        # Resolution
        res_label = ctk.CTkLabel(grid_frame, text="Resolution:", font=FONT_CONFIG["body"])
        res_label.grid(row=0, column=0, sticky="w", padx=(0, SPACING["sm"]), pady=SPACING["sm"])

        resolutions = [(h, l) for h, l in self.format_manager.get_resolution_options()]
        self.resolution_var = ctk.StringVar(value=self.config.default_resolution)
        self.resolution_combo = ctk.CTkComboBox(
            grid_frame,
            values=[label for _, label in resolutions],
            variable=self.resolution_var,
            width=150,
            font=FONT_CONFIG["body"]
        )
        self.resolution_combo.grid(row=0, column=1, padx=SPACING["sm"], pady=SPACING["sm"])

        # Format
        format_label = ctk.CTkLabel(grid_frame, text="Format:", font=FONT_CONFIG["body"])
        format_label.grid(row=0, column=2, sticky="w", padx=(SPACING["lg"], SPACING["sm"]), pady=SPACING["sm"])

        video_formats = self.format_manager.get_video_formats()
        self.format_var = ctk.StringVar(value=self.config.default_format.upper())
        self.format_combo = ctk.CTkComboBox(
            grid_frame,
            values=[f.name for f in video_formats],
            variable=self.format_var,
            width=120,
            font=FONT_CONFIG["body"]
        )
        self.format_combo.grid(row=0, column=3, padx=SPACING["sm"], pady=SPACING["sm"])

        # Audio only checkbox
        self.audio_only_var = ctk.BooleanVar()
        audio_check = ctk.CTkCheckBox(
            grid_frame,
            text="Audio Only (MP3)",
            variable=self.audio_only_var,
            font=FONT_CONFIG["body"],
            command=self._on_audio_mode_change
        )
        audio_check.grid(row=1, column=0, columnspan=2, sticky="w", padx=SPACING["md"], pady=SPACING["sm"])

        # Subtitles checkbox
        self.subtitle_var = ctk.BooleanVar(value=self.config.download_subtitles)
        subtitle_check = ctk.CTkCheckBox(
            grid_frame,
            text="Download Subtitles",
            variable=self.subtitle_var,
            font=FONT_CONFIG["body"]
        )
        subtitle_check.grid(row=1, column=2, columnspan=2, sticky="w", padx=SPACING["md"], pady=SPACING["sm"])

        # Embed subtitles checkbox
        self.embed_subtitle_var = ctk.BooleanVar(value=self.config.embed_subtitles)
        embed_check = ctk.CTkCheckBox(
            grid_frame,
            text="Embed Subtitles",
            variable=self.embed_subtitle_var,
            font=FONT_CONFIG["body"]
        )
        embed_check.grid(row=1, column=2, columnspan=2, sticky="w", padx=SPACING["md"], pady=SPACING["sm"])

        # Configure grid weights
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

    def _create_progress_section(self):
        """Create progress display section"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            frame,
            height=20,
            corner_radius=CORNER_RADIUS["sm"]
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        # Status labels
        status_frame = ctk.CTkFrame(frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["md"]))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=FONT_CONFIG["body"]
        )
        self.status_label.pack(side="left")

        self.speed_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=FONT_CONFIG["caption"]
        )
        self.speed_label.pack(side="right")

    def _create_video_info_section(self):
        """Create video information display with thumbnail"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        # Title
        info_label = ctk.CTkLabel(
            frame,
            text="Video Information",
            font=FONT_CONFIG["heading"]
        )
        info_label.pack(anchor="w", padx=SPACING["md"], pady=SPACING["md"])

        # Info text
        self.info_text = ctk.CTkTextbox(
            frame,
            height=100,
            font=FONT_CONFIG["body"],
            wrap="word"
        )
        self.info_text.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        self.info_text.insert("1.0", "Fetch video info to see details here...")
        self.info_text.configure(state="disabled")

    def _create_buttons_section(self):
        """Create secondary action buttons (Clear, Cancel)"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="x", pady=(0, SPACING["lg"]))

        # Buttons container - align right
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        # Spacer to push buttons to right
        spacer = ctk.CTkLabel(btn_frame, text=" ", width=1)
        spacer.pack(side="left", expand=True)

        # Clear button
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear",
            width=100,
            height=40,
            command=self._clear_all,
            font=FONT_CONFIG["body"],
            fg_color="#757575"
        )
        self.clear_btn.pack(side="right", padx=SPACING["sm"])

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Cancel",
            width=100,
            height=40,
            command=self._cancel_download,
            font=FONT_CONFIG["body"],
            state="disabled",
            fg_color="#e53935",
            hover_color="#c62828"
        )
        self.cancel_btn.pack(side="right")

        # Spacer
        spacer = ctk.CTkLabel(btn_frame, text=" ", width=30)
        spacer.pack(side="left", expand=True)

        # Clear button
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear",
            width=120,
            height=60,
            command=self._clear_all,
            font=("Helvetica", 14, "bold"),
            fg_color="#6d6d6d"
        )
        self.clear_btn.pack(side="right", padx=SPACING["sm"])

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Cancel",
            width=120,
            height=60,
            command=self._cancel_download,
            font=("Helvetica", 14, "bold"),
            state="disabled",
            fg_color="#d32f2f"
        )
        self.cancel_btn.pack(side="right")

    def _create_history_section(self):
        """Create download history section"""
        frame = ctk.CTkFrame(self.main_container)
        frame.pack(fill="both", expand=True)

        # Header with clear button
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        history_label = ctk.CTkLabel(
            header_frame,
            text="Download History",
            font=FONT_CONFIG["heading"]
        )
        history_label.pack(side="left")

        clear_history_btn = ctk.CTkButton(
            header_frame,
            text="Clear All",
            width=100,
            command=self._clear_history,
            font=FONT_CONFIG["caption"]
        )
        clear_history_btn.pack(side="right")

        # History listbox with scrollbar
        self.history_textbox = ctk.CTkTextbox(
            frame,
            font=FONT_CONFIG["body"],
            wrap="word"
        )
        self.history_textbox.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))

    def _bind_events(self):
        """Bind event handlers"""
        pass  # No observers, using direct updates

    def _on_theme_change(self, value):
        """Handle theme change"""
        self.config.theme = value
        save_config(self.config)
        self._setup_theme()
        self.destroy()
        # Note: In production, you'd restart the app or update all widgets

    def _on_audio_mode_change(self):
        """Handle audio-only mode toggle"""
        if self.audio_only_var.get():
            self.format_combo.configure(state="disabled")
            self.resolution_combo.configure(state="disabled")
        else:
            self.format_combo.configure(state="normal")
            self.resolution_combo.configure(state="normal")

    def _paste_url(self):
        """Paste URL from clipboard"""
        try:
            clipboard = self.clipboard_get()
            if clipboard:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clipboard)
        except Exception:
            self._show_error("Clipboard is empty or unavailable")

    def _fetch_info(self):
        """Fetch info - not used anymore, kept for compatibility"""
        pass  # Direct download, no pre-fetch

    def _display_video_info(self, info: VideoInfo):
        """Display video information in textbox and load thumbnail"""
        # Update text info
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")

        view_count = f"{info.view_count:,}" if info.view_count and info.view_count > 0 else "N/A"
        info_str = f"""Title: {info.title}
Uploader: {info.uploader}
Duration: {self._format_duration(info.duration)}
Views: {view_count}
Type: {'Playlist' if info.is_playlist else 'Video'}
ID: {info.id}
"""

        if info.is_playlist:
            info_str += f"Videos in playlist: {info.playlist_count}\n"

        if info.available_formats:
            info_str += f"\nAvailable resolutions: {', '.join(f['resolution'] for f in info.available_formats[:5])}..."

        self.info_text.insert("1.0", info_str)
        self.info_text.configure(state="disabled")

    def _start_download(self):
        """Start download process"""
        print("[DEBUG] _start_download called!")
        import sys
        sys.stdout.flush()

        url = self.url_entry.get().strip()
        print(f"[DEBUG] URL entered: {url}")
        if not url:
            self._show_error("Please enter a URL")
            print("[DEBUG] URL is empty, returning")
            return

        # Get options
        resolution_label = self.resolution_var.get()
        format_name = self.format_var.get().lower()
        download_subtitles = self.subtitle_var.get()
        embed_subtitles = self.embed_subtitle_var.get()
        is_audio_only = self.audio_only_var.get()

        # Map resolution label to height
        resolution_map = {label: height for height, label in self.format_manager.get_resolution_options()}
        resolution = resolution_map.get(resolution_label, "1080")

        # Set engine options
        output_path = self.config.default_download_path
        self.engine.set_download_path(output_path)
        self.engine.set_progress_callback(self._on_engine_progress)

        self._set_ui_state("downloading")
        self.status_label.configure(text="Starting download...")
        self.tracker.state = ProgressState.DOWNLOADING
        self.history.add(DownloadItem(
            url=url,
            title="Downloading...",  # Will be updated after completion
            status=ProgressState.DOWNLOADING,
            progress=0,
            speed="0",
            eta="Starting...",
            filename="",
            output_path=output_path,
            resolution=resolution,
            format="mp3" if is_audio_only else format_name,
            started_at=datetime.now()
        ))

        def worker():
            try:
                print(f"[DEBUG] Starting download: {url}")
                print(f"[DEBUG] Resolution: {resolution}, Format: {format_name}")
                success = self.engine.download(
                    url=url,
                    resolution=resolution,
                    output_format="mp3" if is_audio_only else format_name,
                    output_path=output_path,
                    download_subtitles=download_subtitles,
                    embed_subtitle=embed_subtitles,
                    download_thumbnail=False  # Disabled for speed
                )
                print(f"[DEBUG] Download result: {success}")

                if success:
                    self.after(0, lambda: self._on_download_complete())
                else:
                    self.after(0, lambda: self._on_download_failed("Download failed"))
            except Exception as e:
                print(f"[DEBUG] Exception: {e}")
                self.after(0, lambda: self._on_download_failed(str(e)))

        self._active_thread = threading.Thread(target=worker, daemon=True)
        self._active_thread.start()

    def _on_download_complete(self):
        """Handle download completion"""
        self._set_ui_state("idle")
        self.tracker.state = ProgressState.COMPLETED
        self._show_success("Download completed successfully!")
        self._save_history()

    def _on_download_failed(self, error: str):
        """Handle download failure"""
        self._set_ui_state("idle")
        self.tracker.state = ProgressState.ERROR
        self._show_error(f"Download failed: {error}")
        self._save_history()

    def _cancel_download(self):
        """Cancel current download"""
        if self.is_downloading:
            self.engine.cancel()
            self._set_ui_state("idle")
            self.tracker.state = ProgressState.CANCELLED
            self._show_info("Download cancelled")

    def _clear_all(self):
        """Clear all fields"""
        self.url_entry.delete(0, "end")
        self.current_video_info = None
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", "Fetch video info to see details here...")
        self.info_text.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")
        self.speed_label.configure(text="")
        self.download_btn.configure(state="disabled")
        self.tracker.reset()

    def _clear_history(self):
        """Clear download history"""
        self.history.clear()
        self.history_textbox.delete("1.0", "end")

    def _load_history(self):
        """Load and display history"""
        self._refresh_history_display()

    def _save_history(self):
        """Save history to config"""
        self.config_manager.update(history=self.history.to_list())

    def _refresh_history_display(self):
        """Update history display"""
        self.history_textbox.delete("1.0", "end")
        items = self.history.get_all()

        if not items:
            self.history_textbox.insert("1.0", "No download history")
            return

        for i, item in enumerate(items, 1):
            status_icon = {
                ProgressState.COMPLETED: "✓",
                ProgressState.ERROR: "✗",
                ProgressState.CANCELLED: "⏹",
                ProgressState.DOWNLOADING: "⬇"
            }.get(item.status, "?")

            line = f"{i}. [{status_icon}] {item.title[:50]}...\n"
            line += f"   URL: {item.url}\n"
            line += f"   Status: {item.status.value} | Format: {item.format}@{item.resolution}\n"
            if item.error_message:
                line += f"   Error: {item.error_message}\n"
            line += "\n"
            self.history_textbox.insert("end", line)

    # Removed observer-based progress updates, using direct updates instead

    def _on_engine_progress(self, progress):
        """Handle yt-dlp progress updates - directly update UI"""
        print(f"[DEBUG] Progress: {progress.progress:.1f}% - {progress.speed} - {progress.eta}")

        # Direct UI update (thread-safe via after)
        self.after(0, lambda: self._direct_update_progress(
            progress.progress, progress.speed, progress.eta
        ))

    def _direct_update_progress(self, progress, speed, eta):
        """Directly update progress UI"""
        self.progress_bar.set(progress / 100.0)
        self.status_label.configure(text=f"Downloading: {progress:.1f}%")
        self.speed_label.configure(text=f"{speed} | ETA: {eta}")

    def _set_ui_state(self, state: str):
        """Update UI elements based on state"""
        if state == "downloading":
            self.download_btn.configure(state="disabled")
            self.cancel_btn.configure(state="normal")
            self.is_downloading = True
        else:  # idle
            self.download_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.is_downloading = False

    def _open_settings(self):
        """Open settings window"""
        SettingsWindow(self)

    def _show_error(self, message: str):
        """Show error message"""
        self.status_label.configure(text_color="#f44336")
        self.status_label.configure(text=message)

    def _show_success(self, message: str):
        """Show success message"""
        self.status_label.configure(text_color="#4caf50")
        self.status_label.configure(text=message)

    def _show_info(self, message: str):
        """Show info message"""
        self.status_label.configure(text_color="#2196f3")
        self.status_label.configure(text=message)

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS"""
        if not seconds:
            return "Unknown"
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        if hrs > 0:
            return f"{hrs}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"


class SettingsWindow(ctk.CTkToplevel):
    """Settings dialog"""

    def __init__(self, parent: MainApplication):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("500x550")
        self.resizable(False, False)

        # Center on parent
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._load_settings()

    def _create_widgets(self):
        """Create settings widgets"""
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["lg"])

        # Title
        title = ctk.CTkLabel(container, text="Settings", font=FONT_CONFIG["title"])
        title.pack(pady=(0, SPACING["lg"]))

        # Download Path
        path_frame = ctk.CTkFrame(container, fg_color="transparent")
        path_frame.pack(fill="x", pady=SPACING["sm"])

        ctk.CTkLabel(path_frame, text="Download Path:", font=FONT_CONFIG["body"]).pack(anchor="w")
        self.path_entry = ctk.CTkEntry(path_frame, font=FONT_CONFIG["body"])
        self.path_entry.pack(fill="x", pady=(SPACING["xs"], SPACING["sm"]))

        browse_frame = ctk.CTkFrame(container, fg_color="transparent")
        browse_frame.pack(fill="x")
        ctk.CTkButton(
            browse_frame,
            text="Browse",
            width=100,
            command=self._browse_path,
            font=FONT_CONFIG["body"]
        ).pack(side="right")

        # Separator
        ctk.CTkFrame(container, height=1, fg_color="gray30").pack(fill="x", pady=SPACING["lg"])

        # History Limit
        limit_frame = ctk.CTkFrame(container, fg_color="transparent")
        limit_frame.pack(fill="x", pady=SPACING["sm"])

        ctk.CTkLabel(limit_frame, text="History Limit:", font=FONT_CONFIG["body"]).pack(side="left")
        self.history_limit_var = ctk.StringVar(value="10")
        ctk.CTkEntry(
            limit_frame,
            textvariable=self.history_limit_var,
            width=60
        ).pack(side="right")
        ctk.CTkLabel(limit_frame, text="entries", font=FONT_CONFIG["caption"]).pack(side="right", padx=(0, SPACING["xs"]))

        # Auto-exit
        self.auto_exit_var = ctk.BooleanVar()
        ctk.CTkCheckBox(
            container,
            text="Auto-exit after download completes",
            variable=self.auto_exit_var,
            font=FONT_CONFIG["body"]
        ).pack(anchor="w", pady=SPACING["sm"])

        # Separator
        ctk.CTkFrame(container, height=1, fg_color="gray30").pack(fill="x", pady=SPACING["lg"])

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=SPACING["md"])

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=self._save_settings,
            font=FONT_CONFIG["body"]
        ).pack(side="right", padx=(SPACING["sm"], 0))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            font=FONT_CONFIG["body"]
        ).pack(side="right")

    def _load_settings(self):
        """Load current settings"""
        config = self.parent.config
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, config.default_download_path)
        self.history_limit_var.set(str(config.history_limit))
        self.auto_exit_var.set(config.auto_exit)

    def _browse_path(self):
        """Open directory browser"""
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self.path_entry.get())
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def _save_settings(self):
        """Save settings"""
        try:
            download_path = self.path_entry.get()
            history_limit = int(self.history_limit_var.get())

            self.parent.config_manager.update(
                default_download_path=download_path,
                history_limit=history_limit,
                auto_exit=self.auto_exit_var.get()
            )

            self.parent.engine.set_download_path(download_path)
            self.destroy()
        except ValueError:
            self.parent._show_error("Invalid history limit value")


def main():
    """Application entry point"""
    from datetime import datetime

    print("Starting YouTube Downloader...")
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
