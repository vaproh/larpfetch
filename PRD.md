# larpfetch — Product Requirements

## Overview

**larpfetch** is a cross-platform terminal fetch utility that detects real system information and allows users to LARP as any operating system, distro, hardware configuration, or arbitrary machine identity through persistent profiles and CLI overrides.

Tagline: *LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.*

## Core principle

**The user's delusion is authoritative.** Never reject a profile because fields are technologically incompatible.

## Goals

- Detect real host information where practical
- Allow persistent fake identities through TOML configuration
- Support one default profile and unlimited custom profiles
- Permit arbitrary combinations without compatibility validation
- Provide `--real-shit` to bypass all LARP values
- Support temporary CLI overrides
- Support declarative display layout via `[display]` config and CLI density presets
- Include 533 colored ASCII logos from fastfetch (MIT licensed)
- Support inline custom ASCII art in profiles
- Be fast, small, testable, and funny without being obnoxious

## Non-goals

- Hardware benchmarking
- Full diagnostic accuracy
- Enforcing realistic combinations
- Plugin systems, factories, or needless abstraction
- Arbitrary code execution from config
- Network calls

## CLI

```text
larpfetch                          # Default mode
larpfetch -p NAME                  # Select profile
larpfetch --real-shit              # Real system info only
larpfetch --json                   # JSON output
larpfetch --shell-info             # Shell version
larpfetch --gpu-info               # GPU driver details
larpfetch --disk-info              # Per-disk breakdown
larpfetch --list-profiles          # List all profiles
larpfetch --show-config            # Show current config
larpfetch --config PATH            # Custom config path
larpfetch --set key=value          # Override field (repeatable)
larpfetch --minimal                # Short field preset
larpfetch --compact                # Standard field preset
larpfetch --full                   # Show all fields
larpfetch --generate-config        # Print starter config
larpfetch --color                  # Force color
larpfetch --no-color               # Disable color
larpfetch --version                # Show version
larpfetch --help                   # Show help
```

## Precedence

Normal: `CLI overrides > selected profile > default profile > real values`
Reality: `--real-shit > everything`

## Configuration

TOML at platform-specific paths:

- Linux: `$XDG_CONFIG_HOME/larpfetch/config.toml`
- macOS: `~/Library/Application Support/larpfetch/config.toml`
- Windows: `%APPDATA%\larpfetch\config.toml`

Sections: `[default]`, `[profiles.NAME]`, `[appearance]`, `[display]`

Profiles support a `logo` field (built-in name or inline ASCII art).

`[display]` supports field ordering, custom labels, a custom separator, and hiding unavailable values.

Full config reference: `docs/CONFIG.md`.

## System detection

Best-effort real detection of: username, hostname, OS, distro, kernel, architecture, uptime, shell, CPU, GPU, memory, disk, battery, DE, package manager.

Use `psutil` for portable metrics. Platform-specific probes must fail gracefully.

## Rendering

- ASCII logo paired with aligned key/value rows
- 533 logos with ANSI color support ($1/$2/$3 placeholders)
- Logo selection follows displayed identity (or real identity in `--real-shit`)
- Respect `NO_COLOR`
- ANSI-safe alignment

## Easter eggs

Dry, sparse, deterministic, disableable. No offensive material.

Examples: `Authenticity: N%`, `Source: trust me bro`, `Disappointment: immeasurable`

## Quality

- 241+ tests covering config, display layout, resolution, `--real-shit` invariant, CLI, logos, alignment, easter eggs
- Ruff lint clean
- No eval/exec, no shell=True, no network, no secrets
- Python 3.11+, `psutil` only runtime dependency

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full detailed roadmap.

## Acceptance criteria

1. `pip install larpfetch` installs working `larpfetch` command
2. Works on Linux, macOS, Windows with graceful degradation
3. Default profile overrides real information
4. Custom profiles selectable with `-p`
5. Impossible combinations accepted
6. `--set` temporarily overrides fields
7. `--real-shit` shows only real detected values
8. Logo selection follows displayed identity
9. Tests cover `--real-shit` invariant
10. 533 logos with color support
