# Changelog

## v1.5.1

`--disk-info` disk selection: show the `$HOME` disk by default, or any disk by path, and make it configurable.

- **`--disk-info` defaults to the `$HOME` disk**: with no argument it now shows only the disk that holds `$HOME` (e.g. `/home`), instead of every physical disk.
- **Choose a specific disk by path**: pass an absolute path (e.g. `--disk-info /data`) to show only that disk's usage.
- **Configurable default**: set `disk_info` under `[default]` in your config (value `home`, `physical`, `all`, or a `PATH`) to choose the default breakdown; `--disk-info` overrides it.
- Retains `physical` (all real disks) and `all` (include virtual mounts like tmpfs) modes.
- **Built-in profile expansion**: all profiles enriched with the new fields
  (`architecture`, `resolution`, `terminal`, `wm`, `compositor`, `package_count`)
  and 3 new profiles added (`steamdeck`, `ghostbsd`, `android`) for 13 in total.
- **Renderer alignment fix**: each logo line is now right-padded to a uniform width
  so the info column lines up flush with every logo, regardless of the art's shape.

## v1.5.0

Daily-driver system information: battery state, display resolution, terminal/WM/compositor, device & motherboard model, multi-GPU, and multi-disk modes.

- **Multi-disk + `--disk-info` modes**: `--disk-info` now takes an
  optional mode — `physical` (default: real disks only) or `all` (also lists
  virtual mounts like tmpfs/proc). Virtual filesystems are filtered out of
  `physical` mode. `--disk-info` with no argument defaults to `physical`.
- **Multi-GPU handling**: GPU detection now lists every graphics
  controller (integrated + dedicated + eGPU) joined with ` | ` instead of
  stopping at the first match. `--gpu-info` still appends driver details.
- **Device / motherboard model**: new `device` and `motherboard` fields.
  Linux reads DMI `product_name` / `board_vendor`+`board_name`; macOS uses
  `sysctl hw.model`; Windows queries WMI via PowerShell. All degrade gracefully.
- **DE / WM / compositor**: new `wm` and `compositor` fields. WM detects
  Hyprland/Sway via env and falls back to X11 `_NET_WM_NAME`; compositor reuses
  the WM on Wayland and detects X11 compositors via `_NET_WM_CM_S0`
  (`picom`/`compton`/`xcompmgr`, else `active`). All degrade gracefully.
- **Terminal emulator detection**: a new `terminal` field reports the
  emulator from `TERM_PROGRAM` (e.g. `iTerm`, `WezTerm`), `WT_SESSION`
  (`Windows Terminal`), `TERMINAL`, `COLORTERM`, or `TERM`; degrades gracefully.
- **Display resolution detection**: a new `resolution` field shows the
  primary display resolution, with refresh rate where available
  (`1920x1080 @ 60Hz`). Best-effort per platform — `xrandr` on Linux (with a
  sysfs fallback), `system_profiler` on macOS, `GetSystemMetrics` on Windows —
  and degrades gracefully to an empty value when detection is unavailable.
- **Battery charging/discharging state**: battery now shows
  charge status — e.g. `87% (charging)`, `42% (discharging, 3h 15m left)`,
  `100% (full)`. Detection degrades gracefully when `psutil` is unavailable.

## v1.4.0

Reality vs Delusion: provenance, diff, sources, and shareable profiles.

- `--diff-real`: show only fields where the displayed identity differs from real detection
- `--show-sources`: annotate each displayed value with its origin (real/default/profile/cli)
- `--json --with-sources`: per-field provenance (value, source, real_value) in JSON
- `--export-profile [NAME]`: export real detected system as a shareable standalone profile
- `--profile-file PATH`: load a standalone profile from a TOML file (data-only, no code execution)
- `--inspect-profile NAME|PATH`: inspect a named profile or profile file
- `--check-config`: validate config syntax, unknown sections/keys, and value types
- Provenance tracking in the resolver (`resolve_with_sources`)
- 302 tests (up from 241)

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
