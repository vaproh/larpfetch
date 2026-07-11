"""TOML configuration loading and management."""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from larpfetch.models import FIELD_ALIASES, KNOWN_FIELDS, META_FIELDS, DisplayConfig

# Known top-level config sections
KNOWN_SECTIONS = {"default", "profiles", "appearance", "display"}

# Known appearance keys and their expected types
_APPEARANCE_BOOL_KEYS = {
    "color",
    "show_authenticity",
    "easter_eggs",
    "small",
    "pipe",
}

# Platform default config paths
if sys.platform == "darwin":
    _DEFAULT_CONFIG_DIR = Path.home() / "Library" / "Application Support" / "larpfetch"
elif sys.platform == "win32":
    _DEFAULT_CONFIG_DIR = Path(os.environ.get("APPDATA", "")) / "larpfetch"
    if not str(_DEFAULT_CONFIG_DIR).strip("\\"):
        _DEFAULT_CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "larpfetch"
else:
    _xdg = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    if _xdg.is_absolute():
        _DEFAULT_CONFIG_DIR = _xdg / "larpfetch"
    else:
        _DEFAULT_CONFIG_DIR = Path.home() / ".config" / "larpfetch"

DEFAULT_CONFIG_PATH = _DEFAULT_CONFIG_DIR / "config.toml"


def _resolve_config_path(explicit: str | None = None) -> Path | None:
    """Return the config path to use, or None if no config exists."""
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"Config file not found: {explicit}")
        return p
    if DEFAULT_CONFIG_PATH.is_file():
        return DEFAULT_CONFIG_PATH
    return None


def load_config(path: str | None = None) -> dict[str, Any]:
    """Load and parse a TOML config file.

    Returns a dict with keys: default, profiles, appearance, display.
    Missing sections default to empty dicts.
    Raises FileNotFoundError or tomllib.TOMLDecodeError on failure.
    """
    config_path = _resolve_config_path(path)
    if config_path is None:
        return {"default": {}, "profiles": {}, "appearance": {}, "display": {}}

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    return {
        "default": data.get("default", {}),
        "profiles": data.get("profiles", {}),
        "appearance": data.get("appearance", {}),
        "display": data.get("display", {}),
    }


def get_default_profile(config: dict[str, Any]) -> dict[str, str]:
    """Extract the default profile as a flat string dict."""
    return {k: str(v) for k, v in config.get("default", {}).items()}


def get_named_profiles(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Extract all named profiles as flat string dicts."""
    profiles: dict[str, dict[str, str]] = {}
    for name, values in config.get("profiles", {}).items():
        profiles[name] = {k: str(v) for k, v in values.items()}
    return profiles


def get_appearance(config: dict[str, Any]) -> dict[str, Any]:
    """Extract appearance settings."""
    return config.get("appearance", {})


def get_display_config(config: dict[str, Any]) -> DisplayConfig:
    """Extract display configuration from the [display] section."""
    raw = config.get("display", {})
    fields: list[str] | None = None
    if "fields" in raw:
        fields = [str(f) for f in raw["fields"]]
    field_labels: dict[str, str] | None = None
    if "labels" in raw:
        field_labels = {str(k): str(v) for k, v in raw["labels"].items()}
    separator: str = str(raw.get("separator", ": "))
    hide_unavailable: bool = raw.get("hide_unavailable", False)
    return DisplayConfig(
        fields=fields,
        field_labels=field_labels,
        separator=separator,
        hide_unavailable=hide_unavailable,
    )


def load_profile_file(path: str) -> dict[str, str]:
    """Load a standalone profile from a TOML file.

    Supported formats:
      - Flat top-level scalar key/value pairs, e.g. ``os = "Arch Linux"``
      - A ``[profile]`` table containing the fields

    Standalone profiles are data-only: no code is executed. Nested tables
    other than ``[profile]`` are ignored.

    Raises FileNotFoundError or tomllib.TOMLDecodeError on failure.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Profile file not found: {path}")

    with open(p, "rb") as f:
        data = tomllib.load(f)

    result: dict[str, str] = {}
    profile_table = data.get("profile")
    if isinstance(profile_table, dict):
        for k, v in profile_table.items():
            if not isinstance(v, dict):
                result[str(k)] = str(v)
    else:
        for k, v in data.items():
            if not isinstance(v, dict):
                result[str(k)] = str(v)
    return result


def export_profile_toml(fields: dict[str, str], name: str | None = None) -> str:
    """Render a profile dict as a shareable standalone TOML profile string.

    The result is loadable via ``--profile-file``. When ``name`` is given, a
    commented ``[profiles.NAME]`` block is included for pasting into a config.
    """
    lines = ["# larpfetch profile", "# Load with: larpfetch --profile-file <file>"]
    if name:
        lines.append(f"# Or paste into your config under [profiles.{name}]")
    lines.append("")

    # Ordered fields first, then any extras
    ordered_keys = [k for k in KNOWN_FIELDS if k in fields]
    ordered_keys += [k for k in fields if k not in ordered_keys]

    for k in ordered_keys:
        v = fields[k]
        escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{k} = "{escaped}"')

    return "\n".join(lines) + "\n"


def validate_config(path: str | None = None) -> tuple[list[str], list[str]]:
    """Validate a config file.

    Returns a tuple of (errors, warnings). Errors indicate a config that
    will not behave as intended; warnings indicate likely mistakes.
    Raises FileNotFoundError if an explicit path does not exist.
    """
    errors: list[str] = []
    warnings: list[str] = []

    config_path = _resolve_config_path(path)
    if config_path is None:
        warnings.append("No config file found (using built-in defaults).")
        return errors, warnings

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        errors.append(f"Invalid TOML syntax: {e}")
        return errors, warnings

    # Unknown top-level sections
    for section in data:
        if section not in KNOWN_SECTIONS:
            warnings.append(f"Unknown top-level section '[{section}]'")

    # Appearance validation
    appearance = data.get("appearance", {})
    if isinstance(appearance, dict):
        for key, value in appearance.items():
            if key not in _APPEARANCE_BOOL_KEYS:
                warnings.append(f"Unknown appearance key '{key}'")
            elif not isinstance(value, bool):
                errors.append(f"appearance.{key} must be a boolean")

    # Display validation
    display = data.get("display", {})
    if isinstance(display, dict):
        fields = display.get("fields")
        if fields is not None:
            if not isinstance(fields, list):
                errors.append("display.fields must be a list of strings")
            else:
                valid = set(KNOWN_FIELDS) | set(FIELD_ALIASES) | META_FIELDS
                for f in fields:
                    if not isinstance(f, str):
                        errors.append("display.fields entries must be strings")
                    elif f not in valid:
                        warnings.append(
                            f"display.fields references unknown field '{f}'"
                        )
        if "separator" in display and not isinstance(display["separator"], str):
            errors.append("display.separator must be a string")
        if "hide_unavailable" in display and not isinstance(
            display["hide_unavailable"], bool
        ):
            errors.append("display.hide_unavailable must be a boolean")
        labels = display.get("labels")
        if labels is not None and not isinstance(labels, dict):
            errors.append("display.labels must be a table")

    return errors, warnings
