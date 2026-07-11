"""Data models for larpfetch."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

# Canonical field ordering for display
KNOWN_FIELDS = [
    "username",
    "hostname",
    "os",
    "distro",
    "os_version",
    "kernel",
    "architecture",
    "uptime",
    "shell",
    "terminal",
    "cpu",
    "gpu",
    "memory",
    "disk",
    "disk_detail",
    "resolution",
    "battery",
    "de",
    "wm",
    "compositor",
    "package_manager",
    "package_count",
]

# Fields that are metadata-only and should not be displayed
META_FIELDS = {"logo"}

# Friendly display names
FIELD_LABELS: dict[str, str] = {
    "username": "User",
    "hostname": "Host",
    "os": "OS",
    "distro": "Distro",
    "os_version": "OS Version",
    "kernel": "Kernel",
    "architecture": "Arch",
    "uptime": "Uptime",
    "shell": "Shell",
    "terminal": "Terminal",
    "cpu": "CPU",
    "gpu": "GPU",
    "memory": "Memory",
    "disk": "Disk",
    "disk_detail": "Disk Detail",
    "resolution": "Resolution",
    "battery": "Battery",
    "de": "DE",
    "wm": "WM",
    "compositor": "Compositor",
    "package_manager": "Packages",
    "package_count": "Package Count",
}

# User-friendly aliases for config field references
FIELD_ALIASES: dict[str, str] = {
    "host": "hostname",
    "pkgs": "package_manager",
    "packages": "package_manager",
    "ram": "memory",
    "arch": "architecture",
}

# Density presets
DENSITY_PRESETS: dict[str, list[str]] = {
    "minimal": [
        "os",
        "kernel",
        "uptime",
        "cpu",
        "memory",
        "shell",
    ],
    "compact": [
        "username",
        "hostname",
        "os",
        "kernel",
        "uptime",
        "shell",
        "cpu",
        "gpu",
        "memory",
        "disk",
        "de",
        "package_manager",
        "package_count",
    ],
}


@dataclass
class DisplayConfig:
    """Configuration for how fields are displayed."""

    fields: list[str] | None = None
    field_labels: dict[str, str] | None = None
    separator: str = ": "
    hide_unavailable: bool = False


@dataclass
class SystemInfo:
    """Normalized system/display information.

    Uses an OrderedDict so field iteration is deterministic and follows
    insertion order (which respects KNOWN_FIELDS ordering when populated
    by the collectors).
    """

    fields: OrderedDict[str, str] = field(default_factory=OrderedDict)

    def get(self, key: str, default: str = "") -> str:
        return self.fields.get(key, default)

    def set(self, key: str, value: str) -> None:
        self.fields[key] = value

    def update_from(self, other: dict[str, str]) -> None:
        """Merge other into self. Existing keys are overwritten."""
        for k, v in other.items():
            if v:
                self.fields[k] = v

    def to_dict(self) -> OrderedDict[str, str]:
        return OrderedDict(self.fields)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SystemInfo:
        """Build from a plain dict, coercing values to strings."""
        ordered = OrderedDict()
        for k, v in d.items():
            ordered[k] = str(v)
        return cls(fields=ordered)

    def display_entries(
        self, display_config: DisplayConfig | None = None
    ) -> list[tuple[str, str, str]]:
        """Return (key, label, value) triples in display order.

        Applies the same field selection, aliasing, custom labels, and
        hide_unavailable rules as :meth:`display_items`.
        """
        entries: list[tuple[str, str, str]] = []
        custom_labels = display_config.field_labels if display_config else None
        hide_unavail = display_config.hide_unavailable if display_config else False

        def label_for(key: str) -> str:
            if custom_labels and key in custom_labels:
                return custom_labels[key]
            return FIELD_LABELS.get(key, key.replace("_", " ").title())

        if display_config and display_config.fields is not None:
            field_order = [FIELD_ALIASES.get(f, f) for f in display_config.fields]
            for key in field_order:
                if key not in self.fields:
                    continue
                value = self.fields[key]
                if hide_unavail and not value:
                    continue
                entries.append((key, label_for(key), value))
        else:
            for key in KNOWN_FIELDS:
                if key in self.fields:
                    value = self.fields[key]
                    if hide_unavail and not value:
                        continue
                    entries.append((key, label_for(key), value))
            for key in self.fields:
                if key not in KNOWN_FIELDS and key not in META_FIELDS:
                    value = self.fields[key]
                    if hide_unavail and not value:
                        continue
                    entries.append((key, label_for(key), value))

        return entries

    def display_items(
        self, display_config: DisplayConfig | None = None
    ) -> list[tuple[str, str]]:
        """Return (label, value) pairs in canonical display order.

        If display_config is provided, its fields, labels, and
        hide_unavailable settings override the defaults.
        """
        return [
            (label, value)
            for _key, label, value in self.display_entries(display_config)
        ]
