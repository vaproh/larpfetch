# larpfetch

> **LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

A cross-platform fetch-style terminal system-information utility with one defining gimmick: users can LARP as any operating system, distro, kernel, hardware configuration, hostname, shell, desktop environment, package manager, or arbitrary machine identity.

## Demo

```
        /\          user@btw-i-use-arch
       /  \         --------------------
      /    \        OS: Arch Linux
     /      \       Kernel: 6.99.0-larp
    /   ,,   \      CPU: AMD Ryzen 9 9950X3D
   /   |  |  -\     GPU: NVIDIA RTX 5090
  /_-''    ''-_\   Memory: 4.2 GiB / 128.0 GiB
                  Shell: zsh
                  Authenticity: 3%
```

## Installation

```bash
pipx install larpfetch
```

Or with pip:

```bash
pip install larpfetch
```

## Quick Start

```bash
larpfetch                          # Real system info with arch logo
larpfetch -p nasa                  # LARP as NASA Linux
larpfetch --real-shit              # Real system info only
larpfetch --list-profiles          # See all available profiles
```

## Built-in Profiles

larpfetch ships with these profiles out of the box:

| Profile | Description |
|---------|-------------|
| `nasa` | Quantum Potato 9000, 69 PiB memory |
| `abomination` | Windows kernel + Apple CPU + HolyC shell |
| `hacker` | Parrot OS with RTX 4090 |
| `macbook` | macOS Sequoia with M4 Max |
| `server` | Ubuntu Server, EPYC 9654, 2 TiB RAM |
| `retro` | Windows 98 SE with Voodoo3 |
| `gamer` | Ryzen 9 9950X3D + RTX 5090 |
| `minimal` | Alpine Linux, 512 MiB |
| `templeos` | HolyC on TempleOS |
| `haiku` | Haiku R1/beta4 |

Use them with `-p`:

```bash
larpfetch -p nasa
larpfetch -p abomination
larpfetch -p retro
```

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

[profiles.my-custom]
os = "Custom OS"
cpu = "Custom CPU"

[appearance]
color = true
show_authenticity = true
easter_eggs = true
```

**Platform-specific config locations:**

- Linux: `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml`
- macOS: `~/Library/Application Support/larpfetch/config.toml`
- Windows: `%APPDATA%\larpfetch\config.toml`

## Precedence

Normal mode:

```
CLI overrides > selected profile > default profile > real detected values
```

Reality mode:

```
--real-shit > everything (real values only)
```

## CLI Reference

```bash
larpfetch                              # Default mode
larpfetch -p NAME                      # Select profile
larpfetch --profile NAME               # Select profile (long form)
larpfetch --real-shit                  # Real system info only
larpfetch --list-profiles              # List all profiles
larpfetch --show-config                # Show current config
larpfetch --config /path/to/config.toml  # Custom config path
larpfetch --set key=value              # Override a field (repeatable)
larpfetch --color                      # Force color output
larpfetch --no-color                   # Disable color output
larpfetch --version                    # Show version
larpfetch --help                       # Show help
```

## CLI Overrides

Override any field temporarily:

```bash
larpfetch --set cpu="Quantum Potato 9000"
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"
```

Custom fields are supported. Unknown fields display with auto-formatted labels.

## `--real-shit`

Bypasses all LARP layers and shows real detected system information:

```bash
larpfetch --real-shit
```

This ignores the default profile, selected profile, and CLI `--set` overrides. It does not modify your configuration.

## Color Control

```bash
larpfetch --color       # Force color even when piped
larpfetch --no-color    # Disable all ANSI codes
NO_COLOR=1 larpfetch    # Standard env var (always wins)
```

`NO_COLOR` takes precedence over `--color`.

## Easter Eggs

The output may include occasional humorous lines:

- `Authenticity: N%` - how much of your output is real
- `Source: trust me bro` - triggered by implausible memory values
- `Reality Leakage: 100.00%` - absurdly high package counts
- `Disappointment: immeasurable` - shown in `--real-shit` mode
- `The allegations were true.` - 1% chance based on username

Easter eggs are:

- Deterministic (same input = same output)
- Disableable via `[appearance] easter_eggs = false` or `LARPFETCH_NO_EASTER_EGGS=1`
- Not offensive

## Cross-Platform Support

- **Linux**: Reads `/etc/os-release`, environment variables, `lspci` for GPU
- **macOS**: Uses `platform.mac_ver()`, `system_profiler` for GPU
- **Windows**: Uses `platform` APIs, WMIC for GPU, `COMSPEC` for shell

All platform-specific probes fail gracefully. A missing GPU detector doesn't crash the app.

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

## Development

```bash
git clone <repo>
cd larpfetch
uv venv
uv pip install -e ".[dev]"
pytest
ruff check src/ tests/
```

## Testing

```bash
pytest
pytest --cov=larpfetch
```

Tests cover:

- Config loading and parsing
- Profile resolution and precedence
- `--real-shit` invariant (ignores all fake inputs)
- CLI argument parsing and behavior
- Built-in profiles
- Logo selection
- Renderer output
- Easter egg determinism and env var disabling
- Collector failure degradation
- ANSI-safe alignment
- `NO_COLOR` and `--color`/`--no-color` compliance

## Limitations

- GPU detection is best-effort and platform-dependent
- Package counting is not implemented in v1
- Battery detection requires `psutil` sensor support
- No network calls (by design)
- No hardware benchmarking

## License

MIT
