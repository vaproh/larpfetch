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
    "cpu",
    "gpu",
    "memory",
    "disk",
    "battery",
    "de",
    "package_manager",
    "package_count",
]

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
    "cpu": "CPU",
    "gpu": "GPU",
    "memory": "Memory",
    "disk": "Disk",
    "battery": "Battery",
    "de": "DE",
    "package_manager": "Packages",
    "package_count": "Packages",
}


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

    def display_items(self) -> list[tuple[str, str]]:
        """Return (label, value) pairs in canonical display order."""
        items: list[tuple[str, str]] = []
        # First, known fields in canonical order
        for key in KNOWN_FIELDS:
            if key in self.fields:
                label = FIELD_LABELS.get(key, key.replace("_", " ").title())
                items.append((label, self.fields[key]))
        # Then, any custom fields (deterministic insertion order)
        for key in self.fields:
            if key not in KNOWN_FIELDS:
                label = key.replace("_", " ").title()
                items.append((label, self.fields[key]))
        return items
