# Roadmap

## v1.1.0 — Shipped

- `--logo NAME` flag to pick any logo directly
- `--list-logos` to show all available logo names
- `--list-logos --search <query>` to filter logos
- Pipe mode: suppress logo when stdout is not a TTY
- `--cols N` to force column width
- `--distro NAME` quick distro LARP
- `--small` use small ASCII art variant

## v1.2.0 — Shipped

- JSON output (`--json`)
- Package count detection (apt, pacman, brew, winget)
- `--shell-info` for shell version detection
- `--gpu-info` for detailed GPU detection
- `--disk-info` for per-disk breakdown

## v1.3.0 — Current

- JSON output (`--json`)
- Package count detection (apt, pacman, brew, winget)
- `--shell-info` for shell version detection
- `--gpu-info` for detailed GPU detection
- `--disk-info` for per-disk breakdown

## v1.3.0

- More built-in profiles (gentoo, fedora, debian, opensuse, void, artix, endeavour, manjaro, pop, neon)
- User-contributed logo pack support
- `--compact` mode (no logo, key-value only)

## v2.0.0

- Plugin system for custom collectors
- Custom color themes
- `--format` flag (text, json, yaml)
- `--export-profile` to save current output as a profile
