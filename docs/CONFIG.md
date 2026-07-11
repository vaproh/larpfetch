# Configuration

## Config file location

| Platform | Path |
|----------|------|
| Linux    | `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml` |
| macOS    | `~/Library/Application Support/larpfetch/config.toml` |
| Windows  | `%APPDATA%\larpfetch\config.toml` |

Override with `--config /path/to/config.toml`.

## Structure

A TOML file with four sections: `[default]`, `[profiles.NAME]`, `[appearance]`, and `[display]`.

### `[default]`

Sets fallback values for any field not overridden by a profile or CLI. Supports all known fields:

| Field | Example |
|-------|---------|
| `username` | `"vaproh"` |
| `hostname` | `"btw-i-use-arch"` |
| `os` | `"Arch Linux"` |
| `distro` | `"Arch Linux"` |
| `os_version` | `"24.04 LTS"` |
| `kernel` | `"6.99.0-larp"` |
| `architecture` | `"x86_64"` |
| `uptime` | `"4h 20m"` |
| `shell` | `"zsh"` |
| `cpu` | `"AMD Ryzen 9 9950X3D"` |
| `gpu` | `"NVIDIA RTX 5090"` |
| `memory` | `"128 GiB"` |
| `disk` | `"256 GiB / 1 TiB"` |
| `disk_detail` | `"/: 100 GiB/500 GiB \| /home: 300 GiB/1 TiB"` |
| `battery` | `"98% (charging)"` |
| `resolution` | `"1920x1080 @ 60Hz"` |
| `de` | `"Hyprland"` |
| `wm` | `"Hyprland"` |
| `compositor` | `"Hyprland"` |
| `terminal` | `"kitty"` |
| `device` | `"XPS 13 9310"` |
| `motherboard` | `"Dell Inc. 0PPRXH"` |
| `package_manager` | `"apt btw"` |
| `package_count` | `"6942"` |
| `logo` | `"arch"` |

Custom string fields are also supported — they will display with auto-formatted labels.

### `[profiles.NAME]`

Named profiles selectable with `-p NAME` or `--profile NAME`. Same fields as `[default]`. A profile can also set:

- **`logo`** — reference a built-in logo by name (e.g. `"arch"`, `"ubuntu"`, `"nixos"`) or provide inline ASCII art:

```toml
[profiles.art]
os = "Artistic OS"
logo = """\
    /\\
   /  \\
  /    \\
 /      \\
/________\\
"""
```

Missing fields in a profile inherit from `[default]`, then from real detected values.

### `[appearance]`

Controls rendering behaviour.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `color` | bool | `true` (auto) | Force or disable ANSI color |
| `show_authenticity` | bool | `true` | Show the "Authenticity: N%" line |
| `easter_eggs` | bool | `true` | Enable humorous extra lines |
| `small` | bool | `false` | Always use small ASCII art variants |
| `pipe` | bool | `false` | Suppress logo (auto-set when stdout not a TTY) |

### `[display]`

Controls which fields are shown and how they are labeled.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `fields` | list[str] | `null` | Explicit field order to display |
| `labels` | table | `null` | Custom labels per field key |
| `separator` | str | `": "` | Text between label and value |
| `hide_unavailable` | bool | `false` | Skip empty / unavailable values |

Field names can use aliases like `host`, `ram`, `arch`, `packages`, and `pkgs`.

Example:

```toml
[display]
fields = ["os", "kernel", "cpu", "memory"]
separator = " -> "
hide_unavailable = true

[display.labels]
memory = "RAM"
packages = "Pkgs"
```

## Precedence

Normal mode:

```
CLI overrides > selected profile > default profile > real detected values
```

Reality mode (`--real-shit`):

```
Real values only — bypasses everything
```

CLI density presets (`--minimal`, `--compact`, `--full`) override `[display].fields` for that run.

#### Display density presets

The CLI flags `--minimal`, `--compact`, and `--full` set `fields` to a fixed
list for that invocation:

- `--minimal` → `os, kernel, uptime, cpu, memory, shell`
- `--compact` → common identity + hardware fields, no logo
- `--full` → all fields (default)

Explicit `[display].fields` in the config still applies unless a density flag
is passed.

#### Logo selection

The logo shown follows this priority:

1. `--logo NAME` (CLI, highest)
2. profile `logo` field (built-in name or inline art)
3. real OS (when `--real-shit`)
4. displayed OS/distro

`logo` is a **meta field** — it controls the artwork but is never displayed
as a data row.

## Troubleshooting

- **Config not found:** larpfetch works with zero config (real values only).
  Use `--generate-config` to create one, or `--config PATH` to point at a file.
- **Profile not found:** `--profile foo` errors if `foo` isn't a built-in or
  config profile. List available ones with `--list-profiles`.
- **Logo not found:** if `--logo NAME` or a profile `logo` doesn't match a
  built-in name and isn't inline art, larpfetch falls back to the OS-based logo.
- **`--check-config` reports errors:** fix the TOML — e.g. `color` must be a
  boolean, `[display].fields` must be a list of strings. Warnings (unknown
  sections/keys) are non-fatal.
- **Color looks wrong in a pipe:** color is auto-disabled when stdout isn't a
  TTY and when `NO_COLOR` is set. Force it with `--color`.

## Standalone profile files

In addition to profiles defined in the main config, you can load a profile from a separate file with `--profile-file PATH`. This is how profiles are shared.

Two formats are accepted:

```toml
# Flat format
os = "NASA Linux"
cpu = "Quantum Potato 9000"
logo = "nasa"
```

```toml
# Table format
[profile]
os = "NASA Linux"
cpu = "Quantum Potato 9000"
```

Generate one from your real system with `larpfetch --export-profile [NAME] > myrig.toml`.

**Security:** standalone profiles are data-only. They are parsed with `tomllib` and only scalar key/value pairs are read — loading a profile never executes code, runs commands, or makes network calls. Nested tables other than `[profile]` are ignored.

## Validating your config

Run `larpfetch --check-config` (optionally with `--config PATH`) to validate:

- TOML syntax
- Unknown top-level sections
- Unknown `[appearance]` keys and non-boolean values
- `[display]` field/label/separator types and unknown field references

It exits non-zero if any errors are found.

## Inspecting where values come from

- `larpfetch --show-sources` — annotate each displayed field with `[real]`, `[default]`, `[profile]`, or `[cli]`
- `larpfetch --diff-real` — show only fields where the displayed identity differs from real detection
- `larpfetch --json --with-sources` — machine-readable provenance (`value`, `source`, `real_value`)

## Full example

```toml
[default]
os = "Arch Linux"
distro = "Arch Linux"
hostname = "btw-i-use-arch"
kernel = "6.99.0-larp"
cpu = "AMD Ryzen 9 9950X3D"
gpu = "NVIDIA RTX 5090"
memory = "128 GiB"
shell = "zsh"

[profiles.nasa]
os = "NASA Linux"
distro = "NASA Linux"
cpu = "Quantum Potato 9000"
memory = "69 PiB"
gpu = "Classified"
logo = "nasa"

[profiles.custom]
os = "My Custom OS"
cpu = "Custom CPU"
logo = "arch"
```

## See also

- [USAGE.md](USAGE.md) — full command reference with examples
- [README.md](../README.md) — overview, CLI reference, built-in profiles
- [ROADMAP.md](../ROADMAP.md) — planned features
- [CHANGELOG.md](../CHANGELOG.md) — version history
