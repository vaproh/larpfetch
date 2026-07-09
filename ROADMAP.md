# Roadmap

## v1.0.0 — Current

- Cross-platform system detection (Linux, macOS, Windows)
- 533 ASCII logos with ANSI color support (from fastfetch, MIT)
- 10 built-in LARP profiles
- TOML config with `[default]`, `[profiles]`, `[appearance]`
- `--real-shit` bypass invariant
- `--set` CLI overrides
- Custom ASCII art in profiles
- Easter eggs (deterministic, disableable)
- 197 tests, ruff lint clean

## v1.1.0

- `--logo NAME` flag to pick any logo directly
- `--list-logos` to show all available logo names
- `--list-logos --search <query>` to filter logos
- Pipe mode: suppress logo when stdout is not a TTY
- `--cols N` to force column width

## v1.2.0

- JSON output (`--json`)
- `--shell-info` for shell version detection
- `--gpu-info` for detailed GPU detection
- `--disk-info` for per-disk breakdown
- Package count detection (apt, pacman, brew, winget)

## v1.3.0

- More built-in profiles (gentoo, fedora, debian, opensuse, void, artix, endeavour, manjaro, pop, neon)
- User-contributed logo pack support
- `--compact` mode (no logo, key-value only)

## v2.0.0

- Plugin system for custom collectors
- Custom color themes
- `--format` flag (text, json, yaml)
- `--export-profile` to save current output as a profile
