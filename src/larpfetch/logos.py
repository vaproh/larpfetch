"""ASCII logos for larpfetch."""

from __future__ import annotations

from typing import Dict

# Each logo is a list of strings (lines). All logos must be the same width
# within themselves for clean alignment, but different logos can differ.

LOGOS: Dict[str, list[str]] = {
    "generic": [
        r"    _       _      __       _ ",
        r"   (_)___  (_)____/ /___  (_)",
        r"  / / __ \/ / ___/ / __ \/ / ",
        r" / / / / / / /__/ / / / / /  ",
        r"/_/_/ /_/_/\___/_/_/ /_/_/   ",
    ],
    "arch": [
        r"        /\          ",
        r"       /  \         ",
        r"      /    \        ",
        r"     /      \       ",
        r"    /   ,,   \      ",
        r"   /   |  |  -\     ",
        r"  /_-''    ''-_\   ",
    ],
    "ubuntu": [
        r"          _   _      ",
        r"         | | (_)     ",
        r"  ___  __| | |_  __ _",
        r" / __|/ _` | | |/ _` |",
        r" \__ \ (_| | | | (_| |",
        r" |___/\__,_|_|_|\__,_|",
    ],
    "debian": [
        r"       _____      ",
        r"      /     \     ",
        r"     /  O O  \    ",
        r"    |  \___/  |   ",
        r"     \  ___  /    ",
        r"      |/   \|     ",
        r"   ___/     \___  ",
        r"  /             \ ",
    ],
    "fedora": [
        r"        ______      ",
        r"       /     \     ",
        r"      /       \    ",
        r"     |  O   O  |   ",
        r"     |    __    |   ",
        r"      \  \__/  /    ",
        r"       \______/    ",
    ],
    "windows": [
        r"         _         ",
        r"        | |        ",
        r"  __ _ _| |__   ___",
        r" / _` | | '_ \ / _ \\",
        r" \__,_|_|_| |_|\___/",
        r"                    ",
    ],
    "macos": [
        r"              .:'  ",
        r"          __ :'__  ",
        r"       .'`  `-'  `.",
        r"      :  _______  :",
        r"      : |       | :",
        r"      : |       | :",
        r"      :_|       |_:",
        r"     `-;  `-._.-' ;'",
    ],
    "templeos": [
        r"                  ___  ___  ",
        r"                 /  / /  /  ",
        r"                /  / /  /   ",
        r"    ____       /  / /  /    ",
        r"   /    \    /  / /  /     ",
        r"  /  O O \ /  / /  /      ",
        r"  \  ___  /  / /  /       ",
        r"   |     | /  / /  /      ",
        r"   |     |/  / /  /       ",
        r"   |     /  / /  /        ",
        r"   |     /  / /  /        ",
        r"   |____/  / /  /         ",
    ],
    "nasa": [
        r"     _   ___  ____  ",
        r"    | \ |   \|  _ \ ",
        r"    |  \| |) | | | |",
        r"    |  \  _ <| |_| |",
        r"    |_|\___\_|____/ ",
    ],
    "haiku": [
        r"      ___  ____  ",
        r"     /  / /  /  ",
        r"    /  / /  /   ",
        r"   /  / /  /    ",
        r"  /  / /  /     ",
        r" /  / /  /      ",
        r" \__/ \__/      ",
    ],
}


def _normalize(name: str) -> str:
    """Normalize an OS/distro name for logo lookup."""
    name = name.lower().strip()
    # Direct matches
    if name in LOGOS:
        return name
    # Substring matching
    mappings = [
        ("arch", "arch"),
        ("ubuntu", "ubuntu"),
        ("debian", "debian"),
        ("fedora", "fedora"),
        ("windows", "windows"),
        ("mac", "macos"),
        ("darwin", "macos"),
        ("templeos", "templeos"),
        ("nasa", "nasa"),
        ("haiku", "haiku"),
    ]
    for pattern, logo_key in mappings:
        if pattern in name:
            return logo_key
    return "generic"


def select_logo(displayed_os: str) -> list[str]:
    """Select the appropriate logo based on the displayed OS/distro string."""
    key = _normalize(displayed_os)
    return LOGOS.get(key, LOGOS["generic"])


def get_logo_height(logo: list[str]) -> int:
    return len(logo)


def get_logo_width(logo: list[str]) -> int:
    return max(len(line) for line in logo) if logo else 0
