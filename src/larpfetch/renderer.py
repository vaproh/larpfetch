"""Renderer: produce the final terminal output."""

from __future__ import annotations

import os
import re
import sys
from typing import Any

from larpfetch.easter_eggs import get_authenticity_line, get_extra_lines
from larpfetch.logos import get_logo_width, select_logo
from larpfetch.models import SystemInfo


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _visible_len(text: str) -> int:
    """Return the visible width of a string (without ANSI codes)."""
    return len(_strip_ansi(text))


def _no_color() -> bool:
    """Check if NO_COLOR is set."""
    return os.environ.get("NO_COLOR") is not None


def _should_color() -> bool:
    """Determine if color should be used."""
    if _no_color():
        return False
    if not sys.stdout.isatty():
        return False
    return True


class Colors:
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    DIM = "\033[2m"

    @classmethod
    def disable(cls) -> None:
        attrs = (
            "RESET", "BOLD", "CYAN", "GREEN", "YELLOW",
            "RED", "BLUE", "MAGENTA", "WHITE", "DIM",
        )
        for attr in attrs:
            setattr(cls, attr, "")


def render(
    info: SystemInfo,
    real: SystemInfo,
    real_shit: bool,
    appearance: dict[str, Any] | None = None,
) -> str:
    """Render the full larpfetch output."""
    appearance = appearance or {}
    use_color = appearance.get("color", True) and _should_color()
    show_auth = appearance.get("show_authenticity", True)
    easter_eggs = appearance.get("easter_eggs", True)

    if not use_color:
        Colors.disable()

    # Select logo based on displayed identity (or real identity in --real-shit mode)
    if real_shit:
        display_os = real.get("os", real.get("distro", "Unknown"))
    else:
        display_os = info.get("os", info.get("distro", "Unknown"))

    logo = list(select_logo(display_os))
    logo_height = len(logo)
    logo_width = get_logo_width(logo)

    # Build info lines
    display_items = info.display_items()

    # Username@Hostname header
    username = info.get("username", "unknown")
    hostname = info.get("hostname", "unknown")
    b, c, r = Colors.BOLD, Colors.CYAN, Colors.RESET
    header = f"{b}{c}{username}{r}@{b}{c}{hostname}{r}"
    separator = "-" * _visible_len(f"{username}@{hostname}")

    # Info lines with colors
    info_lines: list[str] = []
    g, w = Colors.GREEN, Colors.WHITE
    rst = Colors.RESET
    for label, value in display_items:
        info_lines.append(f"{g}{label}{rst}: {w}{value}{rst}")

    # Authenticity line
    if show_auth:
        auth_line = get_authenticity_line(real, info, real_shit, easter_eggs)
        if auth_line:
            info_lines.append(f"{Colors.DIM}{auth_line}{Colors.RESET}")

    # Extra easter egg lines
    extras = get_extra_lines(info, real, real_shit, easter_eggs)
    for line in extras:
        info_lines.append(f"{Colors.DIM}{Colors.YELLOW}{line}{Colors.RESET}")

    # Build the final output
    # Ensure logo has enough lines for all content
    total_content = 2 + len(info_lines)  # header + separator + info lines
    while len(logo) < total_content:
        logo.append("")

    # Ensure info has enough lines for the logo
    while len(info_lines) < logo_height - 2:
        info_lines.append("")

    # Align and join
    pad = logo_width + 2  # 2 spaces between logo and info
    output_lines: list[str] = []

    # Header line
    logo_line = logo[0] if logo else ""
    output_lines.append(f"{logo_line}{' ' * (pad - _visible_len(logo_line))}{header}")

    # Separator line
    logo_line = logo[1] if len(logo) > 1 else ""
    dim_rst = f"{Colors.DIM}{separator}{Colors.RESET}"
    output_lines.append(f"{logo_line}{' ' * (pad - _visible_len(logo_line))}{dim_rst}")

    # Info lines
    for i, info_line in enumerate(info_lines):
        logo_line = logo[i + 2] if i + 2 < len(logo) else ""
        output_lines.append(f"{logo_line}{' ' * (pad - _visible_len(logo_line))}{info_line}")

    return "\n".join(output_lines)
