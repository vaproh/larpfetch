"""Profile resolution: merge real values with LARP layers."""

from __future__ import annotations

from larpfetch.models import SystemInfo


def resolve(
    real: SystemInfo,
    default_profile: dict[str, str],
    selected_profile: dict[str, str] | None,
    cli_overrides: dict[str, str],
    real_shit: bool = False,
) -> SystemInfo:
    """Resolve the final display identity.

    Precedence (normal mode):
        CLI overrides > selected profile > default profile > real values

    Reality mode (--real-shit):
        real values only
    """
    if real_shit:
        return real

    # Start from a copy of real values
    resolved = SystemInfo(fields=real.to_dict())

    # Layer 1: default profile
    for k, v in default_profile.items():
        if v:
            resolved.fields[k] = v

    # Layer 2: selected custom profile (inherits from default for missing keys)
    if selected_profile:
        for k, v in selected_profile.items():
            if v:
                resolved.fields[k] = v

    # Layer 3: CLI overrides
    for k, v in cli_overrides.items():
        if v:
            resolved.fields[k] = v

    return resolved
