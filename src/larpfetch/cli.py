"""CLI entry point for larpfetch."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Sequence

from larpfetch import __version__
from larpfetch.collectors.common import collect_all
from larpfetch.config import (
    export_profile_toml,
    get_appearance,
    get_default_profile,
    get_display_config,
    get_named_profiles,
    load_config,
    load_profile_file,
    validate_config,
)
from larpfetch.logos import LOGO_ART
from larpfetch.models import DENSITY_PRESETS
from larpfetch.profiles import get_builtin_profiles
from larpfetch.renderer import render, render_diff, render_sources
from larpfetch.resolver import resolve_with_sources


def _parse_sets(sets: list[str]) -> dict[str, str]:
    """Parse repeated --set key=value arguments."""
    result: dict[str, str] = {}
    for s in sets:
        if "=" not in s:
            print(
                f"Error: --set argument must be key=value, got: {s}",
                file=sys.stderr,
            )
            sys.exit(1)
        key, _, value = s.partition("=")
        key = key.strip()
        if not key:
            print(
                f"Error: --set key cannot be empty in: {s}",
                file=sys.stderr,
            )
            sys.exit(1)
        result[key] = value
    return result


def _get_all_profiles(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Merge built-in profiles with user config profiles.

    User profiles take precedence over built-in profiles.
    """
    profiles = get_builtin_profiles()
    profiles.update(get_named_profiles(config))
    return profiles


def _list_profiles(config: dict[str, Any]) -> None:
    """Print available profiles."""
    profiles = _get_all_profiles(config)
    if not profiles:
        print("No profiles configured.")
        return
    print("Available profiles:")
    for name in sorted(profiles.keys()):
        fields = profiles[name]
        desc = fields.get("os") or fields.get("distro") or "Custom identity"
        print(f"  {name:20s} {desc}")


def _list_logos(search: str | None = None) -> None:
    """Print available logo names."""
    bases = sorted(n for n in LOGO_ART.keys() if not n.endswith("_small"))
    if search:
        search_lower = search.lower()
        bases = [n for n in bases if search_lower in n]
    if not bases:
        print("No logos found.")
        return
    print(f"Available logos ({len(bases)}):")
    for name in bases:
        print(f"  {name}")


def _show_config(config: dict[str, Any]) -> None:
    """Print the resolved configuration."""
    default = get_default_profile(config)
    profiles = _get_all_profiles(config)
    appearance = get_appearance(config)

    def _fmt_val(v: Any) -> str:
        if isinstance(v, bool):
            return str(v).lower()
        return str(v)

    print("Default profile:")
    if default:
        for k, v in sorted(default.items()):
            print(f"  {k} = {_fmt_val(v)}")
    else:
        print("  (empty)")

    print("\nProfiles:")
    if profiles:
        for name in sorted(profiles.keys()):
            print(f"\n  [{name}]")
            for k, v in sorted(profiles[name].items()):
                print(f"    {k} = {_fmt_val(v)}")
    else:
        print("  (none)")

    print("\nAppearance:")
    if appearance:
        for k, v in sorted(appearance.items()):
            print(f"  {k} = {_fmt_val(v)}")
    else:
        print("  (defaults)")


def _inspect_profile(config: dict[str, Any], target: str) -> int:
    """Print details about a named profile or a profile file.

    Returns a process exit code.
    """
    from pathlib import Path

    fields: dict[str, str]
    origin: str

    if Path(target).is_file():
        try:
            fields = load_profile_file(target)
        except Exception as e:  # noqa: BLE001 - surface any load error cleanly
            print(f"Error loading profile file: {e}", file=sys.stderr)
            return 1
        origin = f"file: {target}"
    else:
        builtins = get_builtin_profiles()
        user = get_named_profiles(config)
        if target in user:
            fields = user[target]
            origin = "config"
        elif target in builtins:
            fields = builtins[target]
            origin = "built-in"
        else:
            avail = ", ".join(sorted(set(builtins) | set(user)))
            print(
                f"Error: profile '{target}' not found. Available: {avail}",
                file=sys.stderr,
            )
            return 1

    print(f"Profile: {target} ({origin})")
    logo = fields.get("logo")
    if logo:
        display_logo = logo if "\n" not in logo else "(inline ASCII art)"
        print(f"Logo: {display_logo}")
    print(f"Fields ({len([k for k in fields if k != 'logo'])}):")
    for k in sorted(fields):
        if k == "logo":
            continue
        print(f"  {k} = {fields[k]}")
    return 0


def _check_config(path: str | None) -> int:
    """Validate the config file and print a report. Returns exit code."""
    try:
        errors, warnings = validate_config(path)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nConfig check: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    if warnings:
        print(f"\nConfig check: OK with {len(warnings)} warning(s)")
        return 0
    print("Config check: OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="larpfetch",
        description=(
            "LARP as any distro, hardware, or machine you want."
            " Because reality is optional until you pass --real-shit."
        ),
    )
    parser.add_argument("-p", "--profile", help="Select a named profile")
    parser.add_argument(
        "--real-shit",
        action="store_true",
        help="Show real detected system information only",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available profiles and exit",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration and exit",
    )
    parser.add_argument("--config", help="Path to a custom config file")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override a field (repeatable)",
    )
    parser.add_argument(
        "--distro",
        metavar="NAME",
        help="LARP as a specific distro (e.g. gentoo, fedora, nixos)",
    )
    parser.add_argument(
        "--small",
        action="store_true",
        help="Use small ASCII art variant of the logo",
    )
    parser.add_argument(
        "--logo",
        metavar="NAME",
        help="Pick a specific logo by name",
    )
    parser.add_argument(
        "--list-logos",
        action="store_true",
        help="List available logos and exit",
    )
    parser.add_argument(
        "--search",
        metavar="QUERY",
        help="Search logos when used with --list-logos",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=None,
        metavar="N",
        help="Force column width for the logo",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        default=None,
        help="Force color output even when not a TTY",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=None,
        help="Disable color output",
    )
    parser.add_argument("--version", action="version", version=f"larpfetch {__version__}")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--shell-info",
        action="store_true",
        help="Show shell version in Shell field",
    )
    parser.add_argument(
        "--gpu-info",
        action="store_true",
        help="Show GPU driver details in GPU field",
    )
    parser.add_argument(
        "--disk-info",
        action="store_true",
        help="Show per-disk breakdown",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Show only essential fields (short preset)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Show standard fields without logo",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show all available fields (default behavior)",
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Print a starter config file to stdout",
    )
    parser.add_argument(
        "--diff-real",
        action="store_true",
        help="Show only fields where the displayed identity differs from real",
    )
    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Show where every displayed value came from",
    )
    parser.add_argument(
        "--with-sources",
        action="store_true",
        help="Include per-field provenance in --json output",
    )
    parser.add_argument(
        "--export-profile",
        nargs="?",
        const="",
        default=None,
        metavar="NAME",
        help="Export real detected system as a shareable profile (optional name)",
    )
    parser.add_argument(
        "--profile-file",
        metavar="PATH",
        help="Load a standalone profile from a TOML file",
    )
    parser.add_argument(
        "--inspect-profile",
        metavar="NAME|PATH",
        help="Inspect a named profile or profile file and exit",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate the config file and exit",
    )
    return parser


_GENERATE_CONFIG_TEMPLATE = """# larpfetch configuration
# Place this file at ~/.config/larpfetch/config.toml (Linux),
# ~/Library/Application Support/larpfetch/config.toml (macOS),
# or %APPDATA%\\larpfetch\\config.toml (Windows).

[default]
# Default fallback values for any field
# os = "Gentoo"
# kernel = "6.8.0-custom"

# [profiles.NAME]
# Define named profiles referenced via --profile NAME
# A profile can set any field, plus an optional 'logo' (built-in name
# or inline ASCII art). Missing fields inherit from [default], then real.
# [profiles.templeos]
# os = "TempleOS"
# kernel = "4.14.0-temple"
# shell = "HolyC"
# logo = "templeos"

[appearance]
# General display settings
# color = true       # Force color output
# show_authenticity = false
# easter_eggs = false
# small = false

[display]
# Configure which fields appear and how they're formatted.
# Uncomment to customize. Field names accept aliases like
# 'host', 'ram', 'arch', 'packages', 'pkgs'.

# fields = ["os", "kernel", "uptime", "shell", "cpu", "gpu", "memory"]

# [display.labels]
# Custom labels for fields
# memory = "RAM"
# packages = "Pkgs"

# separator = ": "
# hide_unavailable = false
"""


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Resolve color flag
    force_color: bool | None = None
    if getattr(args, "color", False):
        force_color = True
    if getattr(args, "no_color", False):
        force_color = False

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    # --list-profiles
    if args.list_profiles:
        _list_profiles(config)
        return

    # --list-logos
    if args.list_logos:
        _list_logos(args.search)
        return

    # --show-config
    if args.show_config:
        _show_config(config)
        return

    # --generate-config
    if args.generate_config:
        print(_GENERATE_CONFIG_TEMPLATE)
        return

    # --check-config
    if args.check_config:
        sys.exit(_check_config(args.config))

    # --inspect-profile
    if args.inspect_profile:
        sys.exit(_inspect_profile(config, args.inspect_profile))

    # Collect real system info
    real = collect_all(
        shell_info=args.shell_info,
        gpu_info=args.gpu_info,
        disk_info=args.disk_info,
    )

    # --export-profile: dump real detected system as a shareable profile
    if args.export_profile is not None:
        name = args.export_profile or None
        print(export_profile_toml(dict(real.to_dict()), name), end="")
        return

    # Resolve display identity
    default_profile = get_default_profile(config)
    selected_profile = None
    if not args.real_shit:
        # --profile-file loads a standalone profile
        if args.profile_file:
            try:
                selected_profile = load_profile_file(args.profile_file)
            except FileNotFoundError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error loading profile file: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.profile:
            profiles = _get_all_profiles(config)
            if args.profile not in profiles:
                avail = ", ".join(sorted(profiles.keys()))
                print(
                    f"Error: profile '{args.profile}' not found. Available: {avail}",
                    file=sys.stderr,
                )
                sys.exit(1)
            selected_profile = profiles[args.profile]

    cli_overrides = _parse_sets(args.set)

    # --distro sets distro field as a CLI override
    if args.distro:
        cli_overrides["distro"] = args.distro

    appearance = get_appearance(config)

    # Apply CLI color override to appearance
    if force_color is not None:
        appearance = dict(appearance)
        appearance["color"] = force_color

    resolved, sources = resolve_with_sources(
        real=real,
        default_profile=default_profile,
        selected_profile=selected_profile,
        cli_overrides=cli_overrides,
        real_shit=args.real_shit,
    )

    # Pipe mode: suppress logo when stdout is not a TTY
    if not sys.stdout.isatty():
        appearance = dict(appearance)
        appearance["pipe"] = True

    # Build display config: start from config, then apply density presets
    display_config = get_display_config(config)
    if args.minimal:
        display_config.fields = DENSITY_PRESETS["minimal"]
    elif args.compact:
        display_config.fields = DENSITY_PRESETS["compact"]
    elif args.full:
        display_config.fields = None

    # --json output
    if args.json:
        real_dict = dict(real.to_dict())
        if args.with_sources:
            data: dict[str, Any] = {}
            for key, value in resolved.to_dict().items():
                data[key] = {
                    "value": value,
                    "source": sources.get(key, "real"),
                    "real_value": real_dict.get(key, ""),
                }
            print(json.dumps(data, indent=2))
            return
        out = real_dict if args.real_shit else dict(resolved.to_dict())
        print(json.dumps(out, indent=2))
        return

    # --diff-real: show only differences from real detection
    if args.diff_real:
        print(render_diff(resolved, real, appearance, display_config))
        return

    # --show-sources: annotate each field with its provenance
    if args.show_sources:
        print(render_sources(resolved, sources, appearance, display_config))
        return

    # Render
    output = render(
        resolved,
        real,
        args.real_shit,
        appearance,
        small=args.small,
        logo_name=args.logo,
        cols=args.cols,
        display_config=display_config,
    )
    print(output)


if __name__ == "__main__":
    main()
