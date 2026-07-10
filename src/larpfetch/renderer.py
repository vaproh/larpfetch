"""Renderer: produce the final terminal output."""

from __future__ import annotations

import os
import re
import sys
from typing import Any

from larpfetch.easter_eggs import get_authenticity_line, get_extra_lines
from larpfetch.logos import LOGO_ART, LOGO_COLORS, _normalize, get_logo_width, select_logo
from larpfetch.models import SystemInfo

# Original ANSI color values (never mutated)
_COLOR_VALUES = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "CYAN": "\033[36m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "RED": "\033[31m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "WHITE": "\033[37m",
    "DIM": "\033[2m",
}


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _visible_len(text: str) -> int:
    """Return the visible width of a string (without ANSI codes)."""
    return len(_strip_ansi(text))


def _no_color() -> bool:
    """Check if NO_COLOR is set."""
    return os.environ.get("NO_COLOR") is not None


def _should_color(force_color: bool | None = None) -> bool:
    """Determine if color should be used."""
    if _no_color():
        return False
    if force_color is not None:
        return force_color
    if not sys.stdout.isatty():
        return False
    return True


def _get_colors(use_color: bool) -> dict[str, str]:
    """Return color codes dict. Empty strings if color disabled."""
    if use_color:
        return dict(_COLOR_VALUES)
    return {k: "" for k in _COLOR_VALUES}


def _apply_logo_colors(art: list[str], logo_colors: list[str], use_color: bool) -> list[str]:
    """Replace $1, $2, $3... placeholders in logo art with ANSI color codes.

    $N maps to logo_colors[N-1]. If color is disabled, placeholders are stripped.
    """
    if not use_color:
        # Strip all $N placeholders
        return [re.sub(r"\$\d+", "", line) for line in art]

    result = []
    for line in art:
        styled = line
        for i, color_code in enumerate(logo_colors):
            placeholder = f"${i + 1}"
            if placeholder in styled:
                # Wrap each occurrence: color + text until next placeholder or end
                # Simple approach: replace $N with color, add reset before next $N or at end
                styled = styled.replace(placeholder, color_code)
        # Add reset at end of line if any color was used
        if styled != line:
            styled += "\033[0m"
        result.append(styled)
    return result


def _resolve_logo(
    info: SystemInfo,
    real: SystemInfo,
    real_shit: bool,
    use_color: bool,
    small: bool = False,
    logo_name: str | None = None,
) -> tuple[list[str], list[str]]:
    """Resolve which logo to use, returning (art, colors).

    Priority:
    1. --logo CLI flag (highest)
    2. Profile's 'logo' field (if present and not --real-shit)
    3. Real OS-based selection (if --real-shit)
    4. Displayed OS-based selection
    """
    # --logo flag takes highest priority
    if logo_name:
        if logo_name in LOGO_ART:
            if small:
                small_key = f"{logo_name}_small"
                if small_key in LOGO_ART:
                    return list(LOGO_ART[small_key]), LOGO_COLORS.get(small_key, [])
            return list(LOGO_ART[logo_name]), LOGO_COLORS.get(logo_name, [])
    if real_shit:
        display_os = real.get("os", real.get("distro", "Unknown"))
        if small:
            small_key = f"{_normalize(display_os)}_small"
            if small_key in LOGO_ART:
                return list(LOGO_ART[small_key]), LOGO_COLORS.get(small_key, [])
        art, logo_colors = select_logo(display_os)
        return list(art), logo_colors

    # Check for explicit logo override in the resolved profile
    logo_ref = info.get("logo", "")
    if logo_ref:
        # If it matches a built-in logo name, use it
        if logo_ref in LOGO_ART:
            if small:
                small_key = f"{logo_ref}_small"
                if small_key in LOGO_ART:
                    return list(LOGO_ART[small_key]), LOGO_COLORS.get(small_key, [])
            return list(LOGO_ART[logo_ref]), LOGO_COLORS.get(logo_ref, [])
        # Otherwise, treat as newline-separated custom art (no colors)
        if "\n" in logo_ref:
            return logo_ref.split("\n"), []

    # Fall back to OS-based selection (prefer distro if set to a non-real value)
    display_os = info.get("distro") or info.get("os", "Unknown")
    if small:
        small_key = f"{_normalize(display_os)}_small"
        if small_key in LOGO_ART:
            return list(LOGO_ART[small_key]), LOGO_COLORS.get(small_key, [])
    art, logo_colors = select_logo(display_os)
    return list(art), logo_colors


def render(
    info: SystemInfo,
    real: SystemInfo,
    real_shit: bool,
    appearance: dict[str, Any] | None = None,
    small: bool = False,
    logo_name: str | None = None,
    cols: int | None = None,
) -> str:
    """Render the full larpfetch output."""
    appearance = appearance or {}
    force_color = appearance.get("color")
    use_color = _should_color(force_color)
    show_auth = appearance.get("show_authenticity", True)
    easter_eggs = appearance.get("easter_eggs", True)
    pipe = appearance.get("pipe", False)

    colors = _get_colors(use_color)

    # Config can also set small
    if not small:
        small = appearance.get("small", False)

    logo_raw, logo_colors = _resolve_logo(
        info, real, real_shit, use_color, small=small, logo_name=logo_name,
    )

    # Pipe mode: no logo
    if pipe:
        logo_raw = [""]
        logo_colors = []

    logo = _apply_logo_colors(logo_raw, logo_colors, use_color)
    logo_height = len(logo)
    logo_width = cols if cols is not None else get_logo_width(logo)

    # Derive info text colors from logo palette
    if logo_colors and use_color:
        primary = logo_colors[0]
        secondary = logo_colors[1] if len(logo_colors) > 1 else primary
        info_label_color = primary
        info_value_color = secondary
        header_color = primary
    else:
        info_label_color = colors['GREEN']
        info_value_color = colors['WHITE']
        header_color = colors['CYAN']

    # Build info lines
    display_items = info.display_items()

    # Username@Hostname header
    username = info.get("username", "unknown")
    hostname = info.get("hostname", "unknown")
    header = (
        f"{colors['BOLD']}{header_color}{username}{colors['RESET']}"
        f"@{colors['BOLD']}{header_color}{hostname}{colors['RESET']}"
    )
    separator = "-" * _visible_len(f"{username}@{hostname}")

    # Info lines with logo-derived colors
    info_lines: list[str] = []
    for label, value in display_items:
        line = (
            f"{info_label_color}{label}{colors['RESET']}:"
            f" {info_value_color}{value}{colors['RESET']}"
        )
        info_lines.append(line)

    # Authenticity line
    if show_auth:
        auth_line = get_authenticity_line(real, info, real_shit, easter_eggs)
        if auth_line:
            info_lines.append(f"{colors['DIM']}{auth_line}{colors['RESET']}")

    # Extra easter egg lines
    extras = get_extra_lines(info, real, real_shit, easter_eggs)
    for line in extras:
        info_lines.append(f"{colors['DIM']}{colors['YELLOW']}{line}{colors['RESET']}")

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
    dim_rst = f"{colors['DIM']}{separator}{colors['RESET']}"
    output_lines.append(f"{logo_line}{' ' * (pad - _visible_len(logo_line))}{dim_rst}")

    # Info lines
    for i, info_line in enumerate(info_lines):
        logo_line = logo[i + 2] if i + 2 < len(logo) else ""
        output_lines.append(f"{logo_line}{' ' * (pad - _visible_len(logo_line))}{info_line}")

    return "\n".join(output_lines)
