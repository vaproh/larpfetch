"""Easter eggs and humor for larpfetch."""

from __future__ import annotations

import hashlib
import re

from larpfetch.models import SystemInfo


def _is_implausible_memory(mem: str) -> bool:
    """Check if a memory string is absurdly large (> 1 TiB)."""
    match = re.search(r"([\d.]+)\s*(GiB|TiB|PiB|EiB)", mem, re.IGNORECASE)
    if not match:
        return False
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit == "pib":
        return True
    if unit == "eib":
        return True
    if unit == "tib" and value >= 1:
        return True
    return False


def _compute_authenticity(real: SystemInfo, resolved: SystemInfo, real_shit: bool) -> int:
    """Compute an authenticity percentage (0-100)."""
    if real_shit:
        return 100

    real_d = real.to_dict()
    resolved_d = resolved.to_dict()

    if not real_d:
        return 50

    matches = sum(1 for k in real_d if k in resolved_d and real_d[k] == resolved_d[k])
    total = max(len(real_d), 1)
    pct = int((matches / total) * 100)
    # In LARP mode, authenticity should be low if user is faking a lot
    return max(0, min(100, pct))


def get_authenticity_line(
    real: SystemInfo, resolved: SystemInfo, real_shit: bool, easter_eggs: bool
) -> str | None:
    """Return the authenticity line, or None if disabled."""
    if not easter_eggs:
        return None
    pct = _compute_authenticity(real, resolved, real_shit)
    return f"Authenticity: {pct}%"


def get_extra_lines(
    resolved: SystemInfo, real: SystemInfo, real_shit: bool, easter_eggs: bool
) -> list[str]:
    """Return additional humorous or informational lines."""
    if not easter_eggs:
        return []

    lines: list[str] = []

    if real_shit:
        lines.append("Source: reality (unfortunately)")
        return lines

    # Check for implausible memory
    mem = resolved.get("memory", "")
    if _is_implausible_memory(mem):
        lines.append("Source: trust me bro")

    # Check for absurdly high package count
    pc = resolved.get("package_count", "")
    if pc.isdigit() and int(pc) > 99999:
        lines.append("Reality Leakage: 100.00%")

    # Check if real hardware is better than LARP (out-LARP detection)
    if not real_shit and real.fields:
        # Conservative thresholds for "impressive" real hardware
        real_mem = real.get("memory", "")
        if _is_implausible_memory(real_mem):
            lines.append("Reality has out-LARPed the LARP.")

    # The allegations were true - deterministic based on username
    username = resolved.get("username", "")
    if username:
        h = int(hashlib.md5(username.encode()).hexdigest()[:8], 16)
        if h % 100 == 0:  # 1% chance
            lines.append("The allegations were true.")

    return lines
