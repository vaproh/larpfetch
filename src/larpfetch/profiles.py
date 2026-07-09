"""Built-in profiles that ship with larpfetch."""

from __future__ import annotations

from typing import Any

BUILTIN_PROFILES: dict[str, dict[str, Any]] = {
    "nasa": {
        "os": "NASA Linux",
        "hostname": "mainframe-01",
        "kernel": "5.15.0-nasa-security",
        "cpu": "Quantum Potato 9000",
        "gpu": "Classified",
        "memory": "69 PiB",
        "shell": "nasa-sh",
        "de": "Mission Control Desktop",
        "logo": "nasa",
    },
    "abomination": {
        "os": "Windows 11 Pro",
        "kernel": "6.18.7-arch1-1",
        "cpu": "Apple M7 Ultra",
        "gpu": "NVIDIA RTX 9090 Ti",
        "memory": "69 PiB",
        "shell": "HolyC",
        "de": "GNOME 83",
        "package_manager": "apt btw",
    },
    "hacker": {
        "os": "Parrot OS",
        "distro": "Parrot Security OS 6.3",
        "kernel": "6.9.1-parrot1-amd64",
        "cpu": "Intel Core i9-14900K",
        "gpu": "NVIDIA RTX 4090",
        "memory": "128 GiB",
        "shell": "zsh",
        "de": "KDE Plasma 6",
        "package_manager": "apt",
        "logo": "parrot",
    },
    "macbook": {
        "os": "macOS 15.0 Sequoia",
        "distro": "macOS 15.0",
        "kernel": "Darwin 24.0.0",
        "cpu": "Apple M4 Max",
        "gpu": "Apple M4 Max 40-core",
        "memory": "128 GiB",
        "shell": "zsh",
        "de": "Aqua",
        "logo": "macos",
    },
    "server": {
        "os": "Ubuntu Server 24.04 LTS",
        "distro": "Ubuntu 24.04.1 LTS",
        "kernel": "6.8.0-48-generic",
        "cpu": "AMD EPYC 9654 96-Core",
        "gpu": "None",
        "memory": "2 TiB",
        "shell": "bash",
        "de": "headless",
        "logo": "ubuntu",
    },
    "retro": {
        "os": "Windows 98 SE",
        "kernel": "4.10.2222",
        "cpu": "Intel Pentium III 733MHz",
        "gpu": "3dfx Voodoo3 3000",
        "memory": "256 MiB",
        "shell": "COMMAND.COM",
        "de": "Classic Theme",
        "package_manager": "Manual",
        "logo": "windows95",
    },
    "gamer": {
        "os": "Windows 11 Pro",
        "kernel": "10.0.22631",
        "cpu": "AMD Ryzen 9 9950X3D",
        "gpu": "NVIDIA RTX 5090",
        "memory": "64 GiB",
        "shell": "powershell.exe",
        "de": "Desktop Window Manager",
        "package_manager": "winget",
        "logo": "windows",
    },
    "minimal": {
        "os": "Alpine Linux",
        "distro": "Alpine Linux v3.20",
        "kernel": "6.6.41-0-virt",
        "cpu": "Virtual CPU",
        "memory": "512 MiB",
        "shell": "ash",
        "logo": "alpine",
    },
    "templeos": {
        "os": "TempleOS",
        "distro": "TempleOS v1.0",
        "kernel": "HolyC",
        "cpu": "AMD64 single-core",
        "gpu": "640x480 16-color",
        "memory": "1 GiB",
        "shell": "HolyC",
        "de": "Single Ring, 640x480 16 color",
        "logo": "templeos",
    },
    "haiku": {
        "os": "Haiku",
        "distro": "Haiku R1/beta4",
        "kernel": "14:58",
        "cpu": "Intel Core i5-12400",
        "gpu": "Intel UHD Graphics 730",
        "memory": "16 GiB",
        "shell": "bash",
        "de": "Haiku Desktop",
        "logo": "haiku",
    },
}


def get_builtin_profiles() -> dict[str, dict[str, str]]:
    """Return built-in profiles as string dicts."""
    return {k: {sk: str(sv) for sk, sv in v.items()} for k, v in BUILTIN_PROFILES.items()}


def get_builtin_profile_names() -> list[str]:
    """Return sorted list of built-in profile names."""
    return sorted(BUILTIN_PROFILES.keys())
