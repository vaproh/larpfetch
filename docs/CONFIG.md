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
| `battery` | `"98%"` |
| `de` | `"Hyprland"` |
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

- [README.md](../README.md) — usage, CLI reference, built-in profiles
- [ROADMAP.md](../ROADMAP.md) — planned features
- [CHANGELOG.md](../CHANGELOG.md) — version history
