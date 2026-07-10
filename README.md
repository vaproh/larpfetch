# larpfetch

> **LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

[![asciicast](https://asciinema.org/a/1260535.svg)](https://asciinema.org/a/1260535)

A cross-platform terminal fetch utility that detects real system information and lets you lie about it. Ships with 533 colored ASCII logos from fastfetch and 10 built-in LARP profiles.

## Installation

```bash
uv tool install larpfetch
```

Or with pipx:

```bash
pipx install larpfetch
```

> **Note:** If pipx installs an older version, it may have a stale cache. Fix with:
> ```bash
> pipx uninstall larpfetch && pipx install --index-url https://pypi.org/simple/ larpfetch
> ```

### Upgrade

```bash
uv tool upgrade larpfetch           # uv
pipx upgrade larpfetch              # pipx
```

### Clear cache

```bash
uv cache clean                      # uv
pipx uninstall larpfetch && pipx install larpfetch  # pipx
```

## Usage

```bash
larpfetch                    # Show real system info with auto-detected logo
larpfetch -p nasa            # LARP as NASA Linux
larpfetch -p hacker          # Become a Parrot OS hacker
larpfetch --distro gentoo    # LARP as a specific distro
larpfetch --small            # Use small ASCII art
larpfetch --json             # Output as JSON
larpfetch --shell-info       # Show shell version
larpfetch --gpu-info         # Show GPU driver details
larpfetch --disk-info        # Show per-disk breakdown
larpfetch --real-shit        # Show only real detected values
larpfetch --list-profiles    # List all available profiles
larpfetch --show-config      # Show current configuration
```

### Override any field

```bash
larpfetch --set cpu="Quantum Potato 9000"
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"
larpfetch --distro fedora --set os="Fedora Linux"
```

Custom fields are supported. Unknown fields display with auto-formatted labels.

## Built-in Profiles

| Profile | OS | Highlights |
|---------|-----|------------|
| `nasa` | NASA Linux | Quantum Potato 9000, 69 PiB RAM, Classified GPU |
| `abomination` | Windows 11 Pro | Apple M7 Ultra, HolyC shell, GNOME 83 |
| `hacker` | Parrot OS | RTX 4090, 128 GiB, KDE Plasma 6 |
| `macbook` | macOS Sequoia | M4 Max, 40-core GPU, Aqua DE |
| `server` | Ubuntu Server 24.04 | EPYC 9654, 2 TiB RAM, headless |
| `retro` | Windows 98 SE | Pentium III, Voodoo3, 256 MiB |
| `gamer` | Windows 11 Pro | Ryzen 9 9950X3D, RTX 5090 |
| `minimal` | Alpine Linux | 512 MiB, ash shell |
| `templeos` | TempleOS | HolyC, 640x480 16-color |
| `haiku` | Haiku R1/beta4 | Haiku Desktop |

User-defined profiles in your config file override built-in ones with the same name.

## Configuration

Default config location: `~/.config/larpfetch/config.toml`

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

[profiles.custom]
os = "My Custom OS"
cpu = "Custom CPU"
logo = "arch"                    # Reference a built-in logo by name

[profiles.art]
os = "Artistic OS"
logo = """\
    /\\
   /  \\
  /    \\
 /      \\
/________\\
"""                              # Or inline custom ASCII art

[appearance]
color = true
show_authenticity = true
easter_eggs = true
small = true                          # Always use small ASCII art
```

### Platform-specific config locations

- **Linux**: `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml`
- **macOS**: `~/Library/Application Support/larpfetch/config.toml`
- **Windows**: `%APPDATA%\larpfetch\config.toml`

## Precedence

Normal mode:

```
CLI overrides > selected profile > default profile > real detected values
```

Reality mode (`--real-shit`):

```
Real values only — bypasses everything
```

## Logos

533 ASCII logos adapted from [fastfetch](https://github.com/fastfetch-cli/fastfetch) (MIT licensed), with full ANSI color support. Colors are applied automatically and respect `NO_COLOR`.

Logo selection is based on your displayed identity (or real identity in `--real-shit` mode). Profiles can override the logo by name or provide custom ASCII art.

## Easter Eggs

The output may include occasional humorous lines:

- `Authenticity: N%` — how much of your output is real
- `Source: trust me bro` — triggered by implausible memory values
- `Reality Leakage: 100.00%` — absurdly high package counts
- `Disappointment: immeasurable` — shown in `--real-shit` mode
- `The allegations were true.` — deterministic, based on username hash

Easter eggs are deterministic, disableable via `[appearance] easter_eggs = false` or `LARPFETCH_NO_EASTER_EGGS=1`, and not offensive.

## The Sacred Rule

**The user's delusion is authoritative.**

This is valid:

```
OS: Windows 11 Pro
Kernel: 6.18.7-arch1-1
CPU: Apple M7 Ultra
GPU: NVIDIA RTX 9090 Ti
Memory: 69 PiB
Shell: HolyC
DE: GNOME 83
Package Manager: apt btw
```

Impossible combinations are accepted. Profiles are display identities, not hardware simulations.

## Cross-Platform Support

- **Linux**: `/etc/os-release`, `lspci`, environment variables
- **macOS**: `platform.mac_ver()`, `system_profiler`
- **Windows**: `platform` APIs, WMIC, `COMSPEC`

All platform-specific probes fail gracefully. A missing GPU detector doesn't crash the app.

## CLI Reference

```
larpfetch                              # Default mode
larpfetch -p NAME                      # Select profile
larpfetch --profile NAME               # Select profile (long form)
larpfetch --distro NAME                # LARP as a specific distro
larpfetch --logo NAME                  # Pick a specific logo by name
larpfetch --small                      # Use small ASCII art
larpfetch --cols N                     # Force column width for logo
larpfetch --list-logos                 # List all available logos
larpfetch --list-logos --search ubuntu # Search logos
larpfetch --real-shit                  # Real system info only
larpfetch --json                       # Output as JSON
larpfetch --shell-info                 # Show shell version
larpfetch --gpu-info                   # Show GPU driver details
larpfetch --disk-info                  # Show per-disk breakdown
larpfetch --list-profiles              # List all profiles
larpfetch --show-config                # Show current config
larpfetch --config /path/to/config.toml  # Custom config path
larpfetch --set key=value              # Override a field (repeatable)
larpfetch --color                      # Force color output
larpfetch --no-color                   # Disable color output
larpfetch --version                    # Show version
larpfetch --help                       # Show help
```

## Development

```bash
git clone https://github.com/vaproh/larpfetch.git
cd larpfetch
uv sync
just test
just lint
```

Or with just:

```bash
just dev        # install in dev mode
just test       # run tests
just lint       # ruff check
just fmt        # ruff format
just check      # lint + test
just all        # format + lint + test
```

207 tests covering: config loading, profile resolution, `--real-shit` invariant, CLI parsing, logo selection, ANSI alignment, easter egg determinism, collector degradation, and more.

## Roadmap

- **v1.1**: `--logo`, `--list-logos`, `--cols`, `--distro`, `--small` ✨
- **v1.2**: JSON output, package count, shell/GPU/disk details ✨
- **v1.3**: More profiles, compact mode
- **v2.0**: Plugins, custom themes, export profiles

See [ROADMAP.md](ROADMAP.md) for full details.

## License

MIT — see [LICENSE](LICENSE)
