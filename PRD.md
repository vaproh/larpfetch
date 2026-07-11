# larpfetch — Product Requirements

## Overview

**larpfetch** is a cross-platform terminal fetch utility that detects real system information and lets users LARP as any operating system, distro, hardware configuration, or arbitrary machine identity through persistent profiles, shareable profile files, and CLI overrides.

Tagline: *LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.*

## Maintenance model

larpfetch is 100% made by autonomous coding agents — built, tested, versioned, and published with no human coding or review. The agent operating manual (workflow, definition of done, versioning/release policy) is [AGENTS.md](AGENTS.md); it is the source of truth for how features are implemented and shipped. All work follows the roadmap themes and the quality gate `just check` (ruff + pytest).

## Core principle

**The user's delusion is authoritative.** Never reject a profile because fields are technologically incompatible.

## Goals

Shipped (v1.0 – v1.4):

- Detect real host information where practical
- Persistent fake identities via TOML `[default]` + named `[profiles.NAME]`
- `--real-shit` to bypass all LARP values (the required invariant)
- Temporary CLI overrides via `--set`
- 533 colored ASCII logos from fastfetch (MIT), inline custom ASCII art
- Declarative display layout via `[display]` + CLI density presets
- Provenance: `--show-sources`, `--diff-real`, `--json --with-sources`
- Shareable standalone profile files: `--profile-file`, `--export-profile`, `--inspect-profile`
- `--check-config` validation; `--generate-config` starter file

Planned (see Roadmap):

- More daily-driver fields: battery state, resolution, DE/WM/compositor, terminal emulator, device/mobo model, multi-GPU/multi-disk
- Themes (separate from profiles): built-in palettes, custom colors, field groups, conditional fields, ASCII-only mode, unicode-width correctness
- Diagnostics: `--explain`, `--diagnose`, `--timings`, shell completions, man page
- Privacy/share-aware output: `--privacy`, `--share`

## Non-goals (what not to build)

- GUI — keep it a terminal tool
- Hardware benchmarking
- Full diagnostic accuracy
- Enforcing realistic combinations
- Plugin systems, factories, or needless abstraction
- AI-generated profiles (latency, complexity, privacy)
- A central community registry before demand exists
- Arbitrary code execution from downloaded profiles (serious security risk)
- Public IP detection by default (unnecessary network call + privacy)
- Network calls of any kind
- Matching every single fastfetch field — larpfetch has its own identity
- Hundreds of styling CLI flags — complex styling belongs in configuration

## Scope & phasing

| Phase | Theme | Status |
|-------|-------|--------|
| v1.0 | Core fetch + profiles + 533 logos | Shipped |
| v1.1 | Logo/search/cols/distro/small, pipe mode | Shipped |
| v1.2 | JSON, package count, shell/gpu/disk detail | Shipped |
| v1.3 | Daily-driver customization: display layout, density presets, terminal responsiveness | Shipped |
| v1.4 | Reality vs Delusion: diff, sources, shareable profiles, `--check-config` | Shipped |
| v1.5 | More system fields: battery, resolution, DE/WM, terminal, device model | Planned |
| v1.6 | Themes and visual polish | Planned |
| v1.7 | Diagnostics: `--explain`, `--diagnose`, `--timings`, completions | Planned |
| v1.8 | Deeper platform: privacy, multi-GPU/disk, per-manager counts | Planned |
| v2.0 | Stability: stable JSON/config/profile schemas, migration, CI | Planned |

Full detail: [ROADMAP.md](ROADMAP.md).

## CLI

```text
Identity
  larpfetch -p NAME              # Select a named profile
  larpfetch --profile NAME        # (long form)
  larpfetch --profile-file PATH   # Load a standalone profile file
  larpfetch --distro NAME         # LARP as a specific distro
  larpfetch --logo NAME           # Pick a logo by name
  larpfetch --set key=value       # Override a field (repeatable)
  larpfetch --real-shit           # Real system info only

Output modes
  larpfetch --json                # JSON output
  larpfetch --with-sources        # Per-field provenance in JSON
  larpfetch --diff-real           # Only fields that differ from real
  larpfetch --show-sources        # Annotate each value's origin
  larpfetch --minimal             # Short field preset
  larpfetch --compact             # Standard fields, no logo
  larpfetch --full                # All available fields
  larpfetch --color / --no-color  # Force / disable color
  larpfetch --small               # Small ASCII art variant
  larpfetch --cols N              # Force logo column width

Info detail
  larpfetch --shell-info          # Shell version
  larpfetch --gpu-info            # GPU driver details
  larpfetch --disk-info           # Per-disk breakdown

Profiles & config
  larpfetch --list-profiles       # List all profiles
  larpfetch --show-config         # Show current config
  larpfetch --inspect-profile NAME|PATH  # Inspect a profile/file
  larpfetch --export-profile [NAME]      # Export real system as a profile
  larpfetch --check-config        # Validate the config file
  larpfetch --generate-config     # Print a starter config
  larpfetch --config PATH         # Custom config path
  larpfetch --list-logos [--search QUERY]  # List / search logos
  larpfetch --version             # Show version
  larpfetch --help                # Show help
```

## Precedence

Normal: `CLI overrides > selected profile (or --profile-file) > default profile > real values`

Reality: `--real-shit > everything` (profiles and overrides are fully bypassed)

## Configuration

TOML at platform-specific paths:

- Linux: `$XDG_CONFIG_HOME/larpfetch/config.toml`
- macOS: `~/Library/Application Support/larpfetch/config.toml`
- Windows: `%APPDATA%\larpfetch\config.toml`

Sections: `[default]`, `[profiles.NAME]`, `[appearance]`, `[display]`.

Profiles support a `logo` field (built-in name or inline ASCII art). `[display]` controls field order, custom labels, separator, and hiding unavailable values. Standalone profile files are data-only TOML (flat or under `[profile]`), never executed.

Full config reference: [docs/CONFIG.md](docs/CONFIG.md). Architecture: [docs/architecture.md](docs/architecture.md).

## System detection

Best-effort real detection of: username, hostname, OS, distro, kernel, architecture, uptime, shell, CPU, GPU, memory, disk, battery, DE, package manager.

Use `psutil` for portable metrics. Platform-specific probes must fail gracefully (return an unavailable value, never crash).

## Rendering

- ASCII logo paired with aligned key/value rows
- 533 logos with ANSI color support ($1/$2/$3 placeholders)
- Logo selection follows displayed identity (or real identity in `--real-shit`)
- Respect `NO_COLOR`; count visible width (not ANSI length) for alignment
- Terminal-width-aware: drop/smallen the logo on narrow terminals
- Profiles can override the logo by name or provide custom art

## Easter eggs

Dry, sparse, deterministic, disableable. No offensive material.

Examples: `Authenticity: N%`, `Source: trust me bro`, `Disappointment: immeasurable`

## Architecture

See [docs/architecture.md](docs/architecture.md) for the module map, data flow, resolution algorithm, and security model.

## Quality

- 300+ tests covering config, display layout, provenance tracking, profile resolution, `--real-shit` invariant, CLI, logos, alignment, easter eggs
- Ruff lint clean
- No eval/exec, no shell=True, no network, no secrets
- Python 3.11+, `psutil` only runtime dependency

## Acceptance criteria

1. `pip install larpfetch` installs a working `larpfetch` command
2. Works on Linux, macOS, Windows with graceful degradation
3. Default profile overrides real information
4. Custom profiles selectable with `-p` / `--profile`
5. Impossible combinations accepted
6. `--set` temporarily overrides fields
7. `--real-shit` shows only real detected values and bypasses all profiles/overrides
8. Logo selection follows displayed identity
9. Tests cover the `--real-shit` invariant
10. 533 logos with color support
11. `--show-sources` / `--diff-real` reveal the real-vs-delusion gap
12. Standalone profile files load without executing code
