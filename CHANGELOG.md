# Changelog

## v1.3.0

- Declarative `[display]` config section with field ordering, labels, separator, and hide-unavailable
- CLI density presets: `--minimal`, `--compact`, `--full`
- `--generate-config` starter config output
- Terminal-width-aware logo suppression
- 241 tests

## v1.2.0

- `--json` flag for JSON output
- Package count detection (apt, pacman, rpm, brew, winget)
- `--shell-info`: show shell version alongside shell name
- `--gpu-info`: show GPU driver details
- `--disk-info`: per-disk usage breakdown
- `disk_detail` field added to known fields
- 207 tests (up from 197)

## v1.1.2

- Increase logo-info spacing to 4 characters

## v1.1.1

- Fix `get_logo_width()` to use ANSI-stripping visible length
- Restore TTY-based auto-detection for color output

## v1.1.0

- `--logo NAME` flag to pick any logo directly
- `--list-logos` / `--list-logos --search <query>`
- `--cols N` to force column width
- `--distro NAME` quick distro LARP
- `--small` use small ASCII art variant
- Pipe mode: suppress logo when stdout is not a TTY

## v1.0.0

- Initial release on PyPI
- 533 ASCII logos from fastfetch (MIT)
- 10 built-in LARP profiles (nasa, abomination, hacker, macbook, server, retro, gamer, minimal, templeos, haiku)
- TOML config with `[default]`, `[profiles]`, `[appearance]` sections
- CLI: `-p`, `--real-shit`, `--set`, `--list-profiles`, `--show-config`, `--config`, `--color`, `--no-color`, `--version`, `--help`
- Easter eggs (authenticity %, Source: trust me bro, etc.)
- Cross-platform support (Linux, macOS, Windows)
- 197 tests
