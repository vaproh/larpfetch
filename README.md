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
pipx install .
```

Or with pip:

```bash
pip install .
```

## Usage

```bash
larpfetch                          # Use default profile
larpfetch -p nasa                  # Select a named profile
larpfetch --real-shit              # Show real system info only
larpfetch --list-profiles          # List available profiles
larpfetch --show-config            # Show current configuration
larpfetch --config /path/to/config.toml
larpfetch --set cpu="Quantum Potato 9000"
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"
larpfetch --version
larpfetch --help
```

## Profiles

Create a `~/.config/larpfetch/config.toml` (or `$XDG_CONFIG_HOME/larpfetch/config.toml`):

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
hostname = "mainframe-01"
cpu = "Quantum Potato 9000"
gpu = "Classified"
memory = "69 PiB"

[profiles.abomination]
os = "Windows 11 Pro"
kernel = "6.18.7-arch1-1"
cpu = "Apple M7 Ultra"
gpu = "NVIDIA RTX 9090 Ti"
shell = "HolyC"
de = "GNOME 83"
package_manager = "apt btw"

[appearance]
color = true
show_authenticity = true
easter_eggs = true
```

## Configuration

**Default config locations:**

- Linux: `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml`
- macOS: `~/Library/Application Support/larpfetch/config.toml`
- Windows: `%APPDATA%\larpfetch\config.toml`

**Precedence (normal mode):**

```
CLI overrides > selected custom profile > default profile > real detected values
```

**Reality mode (`--real-shit`):**

```
Real detected values only
```

The user's delusion is authoritative. Impossible combinations are accepted. Windows 11 with an Arch kernel and Apple M7 Ultra CPU? Valid. You do you.

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

## Cross-Platform Support

- **Linux**: Reads `/etc/os-release`, environment variables, `lspci` for GPU
- **macOS**: Uses `platform.mac_ver()`, `system_profiler` for GPU
- **Windows**: Uses `platform` APIs, WMIC for GPU

All platform-specific probes fail gracefully. A missing GPU detector doesn't crash the app.

## Easter Eggs

The output may include occasional humorous lines. Easter eggs are:

- Deterministic (same input = same output)
- Disableable via `[appearance] easter_eggs = false` or `NO_COLOR`
- Not offensive
- Not random (unless testable)

Some are triggered by specific profile values. Discover them yourself.

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
- Logo selection
- Renderer output
- Easter egg determinism
- Collector failure degradation
- ANSI-safe alignment
- `NO_COLOR` compliance

## Limitations

- GPU detection is best-effort and platform-dependent
- Package counting is not implemented in v1 (no safe universal method)
- Battery detection requires `psutil` sensor support
- No network calls (by design)
- No hardware benchmarking

## License

MIT
