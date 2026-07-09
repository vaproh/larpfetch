"""TOML configuration loading and management."""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path
from typing import Any

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

    Returns a dict with keys: default, profiles, appearance.
    Missing sections default to empty dicts.
    Raises FileNotFoundError or tomllib.TOMLDecodeError on failure.
    """
    config_path = _resolve_config_path(path)
    if config_path is None:
        return {"default": {}, "profiles": {}, "appearance": {}}

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    return {
        "default": data.get("default", {}),
        "profiles": data.get("profiles", {}),
        "appearance": data.get("appearance", {}),
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
