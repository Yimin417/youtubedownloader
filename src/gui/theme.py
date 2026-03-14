"""
Theme configuration for CustomTkinter application
"""
import customtkinter as ctk


# Color schemes
DARK_THEME = {
    "fg_color": "#1a1a2e",
    "bg_color": "#16213e",
    "accent_color": "#e94560",
    "secondary_accent": "#0f3460",
    "text_color": "#ffffff",
    "disabled_color": "#4a4a6a",
    "success_color": "#4caf50",
    "error_color": "#f44336",
    "warning_color": "#ff9800",
    "info_color": "#2196f3",
}

LIGHT_THEME = {
    "fg_color": "#f5f5f5",
    "bg_color": "#ffffff",
    "accent_color": "#e94560",
    "secondary_accent": "#e0e0e0",
    "text_color": "#1a1a2e",
    "disabled_color": "#b0b0b0",
    "success_color": "#4caf50",
    "error_color": "#f44336",
    "warning_color": "#ff9800",
    "info_color": "#2196f3",
}


def setup_theme(theme: str = "dark"):
    """
    Setup CustomTkinter theme

    Args:
        theme: "dark" or "light"
    """
    colors = DARK_THEME if theme == "dark" else LIGHT_THEME

    ctk.set_appearance_mode(theme)
    ctk.set_default_color_theme("blue")

    # CustomTkinter doesn't have global widget color settings in v5
    # Colors are applied per-widget in the application


def get_theme_colors(theme: str = "dark") -> dict:
    """Get theme color dictionary"""
    return DARK_THEME.copy() if theme == "dark" else LIGHT_THEME.copy()


# Font configuration
FONT_CONFIG = {
    "title": ("Helvetica", 24, "bold"),
    "heading": ("Helvetica", 16, "bold"),
    "subtitle": ("Helvetica", 14),
    "body": ("Helvetica", 12),
    "caption": ("Helvetica", 10),
    "mono": ("Consolas", 11),
}


# Spacing configuration
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}


# Corner radius
CORNER_RADIUS = {
    "sm": 4,
    "md": 8,
    "lg": 12,
}
