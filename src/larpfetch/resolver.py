"""Profile resolution: merge real values with LARP layers."""

from __future__ import annotations

from larpfetch.models import SystemInfo

# Provenance sources, ordered by increasing precedence.
SOURCE_REAL = "real"
SOURCE_DEFAULT = "default"
SOURCE_PROFILE = "profile"
SOURCE_CLI = "cli"


def resolve_with_sources(
    real: SystemInfo,
    default_profile: dict[str, str],
    selected_profile: dict[str, str] | None,
    cli_overrides: dict[str, str],
    real_shit: bool = False,
) -> tuple[SystemInfo, dict[str, str]]:
    """Resolve the final display identity and track each field's source.

    Returns a tuple of (resolved SystemInfo, sources) where sources maps
    each field key to one of the SOURCE_* constants.

    Precedence (normal mode):
        CLI overrides > selected profile > default profile > real values

    Reality mode (--real-shit):
        real values only
    """
    resolved = SystemInfo()
    sources: dict[str, str] = {}

    # Layer 0: real values (always the base)
    for k, v in real.to_dict().items():
        resolved.fields[k] = v
        sources[k] = SOURCE_REAL

    if real_shit:
        return resolved, sources

    # Layer 1: default profile
    for k, v in default_profile.items():
        if v:
            resolved.fields[k] = v
            sources[k] = SOURCE_DEFAULT

    # Layer 2: selected custom profile (inherits from default for missing keys)
    if selected_profile:
        for k, v in selected_profile.items():
            if v:
                resolved.fields[k] = v
                sources[k] = SOURCE_PROFILE

    # Layer 3: CLI overrides
    for k, v in cli_overrides.items():
        if v:
            resolved.fields[k] = v
            sources[k] = SOURCE_CLI

    return resolved, sources


def resolve(
    real: SystemInfo,
    default_profile: dict[str, str],
    selected_profile: dict[str, str] | None,
    cli_overrides: dict[str, str],
    real_shit: bool = False,
) -> SystemInfo:
    """Resolve the final display identity.

    Thin wrapper over :func:`resolve_with_sources` that discards provenance.
    """
    resolved, _ = resolve_with_sources(
        real=real,
        default_profile=default_profile,
        selected_profile=selected_profile,
        cli_overrides=cli_overrides,
        real_shit=real_shit,
    )
    return resolved
