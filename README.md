# larpfetch

> **LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

> **100% made by autonomous coding agents** — no human writes code here. See [AGENTS.md](AGENTS.md) for the operating manual.

> If you like this project, drop a ⭐ on [GitHub](https://github.com/vaproh/larpfetch) — it helps others find it.

[![PyPI - Version](https://img.shields.io/pypi/v/larpfetch?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/larpfetch/)
[![GitHub License](https://img.shields.io/github/license/vaproh/larpfetch?style=flat-square)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/vaproh/larpfetch?style=flat-square&logo=git&logoColor=white)](https://github.com/vaproh/larpfetch/commits/main)
[![Built with Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Powered by psutil](https://img.shields.io/badge/powered%20by-psutil-00ADD8?style=flat-square)](https://github.com/giampaolo/psutil)
[![Logos from fastfetch](https://img.shields.io/badge/logos-fastfetch-FF6B6B?style=flat-square)](https://github.com/fastfetch-cli/fastfetch)
[![100% Autonomous](https://img.shields.io/badge/100%25%20made%20by-autonomous%20agents-9b59b6?style=flat-square)](AGENTS.md)

A cross-platform terminal fetch utility that detects real system information and lets you lie about it. Ships with 533 colored ASCII logos from fastfetch and 13 built-in LARP profiles.

## Demo

<p align="center">
  <img src="assets/demo.gif" alt="larpfetch demo" width="816">
</p>

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
larpfetch --diff-real        # Show only what differs from reality
larpfetch --show-sources     # Show where each value came from
larpfetch --shell-info       # Show shell version
larpfetch --gpu-info         # Show GPU driver details
larpfetch --disk-info        # Show per-disk breakdown (disk holding $HOME by default)
larpfetch --disk-info /data   # Show only the /data disk
larpfetch --disk-info all     # Include virtual mounts (tmpfs, proc, …)
larpfetch --minimal          # Show a short field set
larpfetch --compact          # Show standard fields without the logo
larpfetch --full             # Show all fields
larpfetch --real-shit        # Show only real detected values
larpfetch --list-profiles    # List all available profiles
larpfetch --show-config      # Show current configuration
larpfetch --generate-config  # Print a starter config
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
| `steamdeck` | SteamOS 3.6 | AMD Custom Zen 2, RDNA 2 |
| `ghostbsd` | GhostBSD 24.04 | Intel Core i7, UHD Graphics 770 |
| `android` | Android 14 | Snapdragon 8 Gen 3, Adreno 750 |

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

[display]
fields = ["os", "kernel", "cpu", "memory"]
separator = " -> "
hide_unavailable = true

[display.labels]
memory = "RAM"
```

### Platform-specific config locations

- **Linux**: `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml`
- **macOS**: `~/Library/Application Support/larpfetch/config.toml`
- **Windows**: `%APPDATA%\larpfetch\config.toml`

For the full config reference (all fields, appearance options, profiles, inline logos), see [docs/CONFIG.md](docs/CONFIG.md). For a complete command reference, see [docs/USAGE.md](docs/USAGE.md).

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

## Not just a meme

larpfetch is funny on purpose, but it's a real daily-driver fetch tool underneath:

- Detects your actual system with `psutil` and platform-specific probes
- Clean, aligned, color-aware output that respects `NO_COLOR` and narrow terminals
- Scriptable: `--json`, `--minimal`, `--compact`, `--full`, and automatic pipe mode
- Fully customizable: declarative `[display]` config, named profiles, and CLI overrides
- Cross-platform (Linux, macOS, Windows) with graceful degradation

### Reality vs delusion

By default larpfetch shows your LARP identity. `--real-shit` shows only detected truth. The contrast is the whole point:

| Field  | Real (`--real-shit`)     | Delusion (`-p nasa`)        |
|---------|---------------------------|-----------------------------|
| OS      | Arch Linux               | NASA Linux                  |
| CPU     | Ryzen 7 7840HS          | Quantum Potato 9000        |
| Memory  | 32 GiB                   | 69 PiB                      |
| GPU     | Radeon 780M              | Classified                 |

`--diff-real` prints exactly these differences inline, and `--show-sources` annotates where every value came from:

```bash
larpfetch -p nasa --diff-real      # only the fields you're lying about
larpfetch -p nasa --show-sources   # [real] / [default] / [profile] / [cli] per field
```

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
larpfetch --json --with-sources        # JSON with per-field provenance
larpfetch --diff-real                  # Show only fields that differ from real
larpfetch --show-sources               # Show where each value came from
larpfetch --shell-info                 # Show shell version
larpfetch --gpu-info                   # Show GPU driver details
larpfetch --disk-info                  # Show per-disk breakdown ($HOME disk by default)
larpfetch --disk-info /data            # Show only the /data disk
larpfetch --disk-info all              # Include virtual mounts
larpfetch --minimal                    # Short field preset
larpfetch --compact                    # Standard fields, no logo
larpfetch --full                       # All available fields
larpfetch --export-profile [NAME]      # Export real system as a shareable profile
larpfetch --profile-file PATH          # Load a standalone profile file
larpfetch --inspect-profile NAME|PATH  # Inspect a profile or profile file
larpfetch --list-profiles              # List all profiles
larpfetch --show-config                # Show current config
larpfetch --generate-config            # Print a starter config
larpfetch --check-config               # Validate the config file
larpfetch --config /path/to/config.toml  # Custom config path
larpfetch --set key=value              # Override a field (repeatable)
larpfetch --color                      # Force color output
larpfetch --no-color                   # Disable color output
larpfetch --version                    # Show version
larpfetch --help                       # Show help
```

## Sharing profiles

Export your real system as a standalone profile, then share the file. Profiles are data-only TOML — loading one never executes code.

```bash
larpfetch --export-profile myrig > myrig.toml   # capture your real system
larpfetch --profile-file myrig.toml             # someone else LARPs as your rig
larpfetch --inspect-profile myrig.toml          # see what a profile contains
```

## Resources

- [Usage docs](docs/USAGE.md) — full command reference with examples
- [Configuration docs](docs/CONFIG.md) — full config reference
- [Architecture](docs/architecture.md) — module map and data flow
- [Changelog](CHANGELOG.md) — version history
- [Roadmap](ROADMAP.md) — planned features

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

361 tests covering: config loading, display layout, profile resolution, provenance tracking, `--real-shit` invariant, CLI parsing, logo selection, ANSI alignment, easter egg determinism, collector degradation, and more.

> **Maintenance:** This project is 100% made by autonomous coding agents — developed, tested, and released without any human coding. The authoritative operating manual for that process lives in [AGENTS.md](AGENTS.md).

## Roadmap

| Release | Theme |
|---------|-------|
| **v1.1** | `--logo`, `--list-logos`, `--cols`, `--distro`, `--small` ✨ |
| **v1.2** | JSON output, package count, shell/GPU/disk details ✨ |
| **v1.3** | Daily-driver customization — declarative display, density presets, terminal responsiveness ✨ |
| **v1.4** | Reality vs delusion — `--diff-real`, `--show-sources`, shareable profiles ✨ |
| **v1.5** | Daily-driver system info — battery state, resolution, terminal/WM/compositor, device & motherboard, multi-GPU, multi-disk ✅ (v1.5.1: `--disk-info` defaults to `$HOME` disk, takes a PATH, configurable) |
| **v1.6** | Themes and visual polish — catppuccin, dracula, nord, gruvbox |
| **v1.7** | Diagnostics — `--explain`, `--diagnose`, `--timings`, shell completions |
| **v2.0** | Stability — stable JSON/config schemas, cross-platform CI, performance targets |

See [ROADMAP.md](ROADMAP.md) for the full detailed roadmap.

## 💰 Support

If you found my work helpful, feel free to support:

### One-time

[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/vaproh)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/vaproh)

### Crypto

**Ethereum (ERC-20)** `0xD78C15C6932356e57c75a050a602474372804714`

**BNB Smart Chain (BEP-20)** `0xD78C15C6932356e57c75a050a602474372804714`

**Solana** `CvAZzE6jTwxQq1npGzeoTBByj7Ap4REmuukf3BeiuyHi`

**Bitcoin (BTC)** `bc1q7tct80xelr57zdmvcux495dec8l4m2t8eqdzn4`

**Tron (TRC-20)** `TKvaQHMqvzeX2UAz6Cz2WRckRh28Hjd2Xy`

**Litecoin (LTC)** `LXYZJ754RdVXzLkoKVA91wTYjYfRyxQ9pA`

**Zcash** `t1bFWcooKThyQjQzrJACXXCYbNZLS7QUzmF`

## License

MIT — see [LICENSE](LICENSE)
