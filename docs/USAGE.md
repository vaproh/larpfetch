# Usage

A complete command reference for `larpfetch`. For configuration syntax, see
[CONFIG.md](CONFIG.md). For internals, see [architecture.md](architecture.md).

## Quick start

```bash
larpfetch                 # real system info, auto-detected logo
larpfetch -p nasa         # LARP as a built-in profile
larpfetch --real-shit     # only real detected values
```

## Command reference

Flags are grouped by purpose. All flags are optional; running `larpfetch` with
no arguments shows your real system with the matching logo.

### Identity & profiles

| Flag | Description |
|------|-------------|
| `-p NAME`, `--profile NAME` | Select a built-in or config-defined profile |
| `--profile-file PATH` | Load a standalone profile from a TOML file |
| `--distro NAME` | LARP as a specific distro (shortcut for `--set distro=NAME`) |
| `--logo NAME` | Force a specific logo by name (overrides profile/default) |
| `--set key=value` | Override a single field (repeatable) |

Examples:

```bash
# Pick a profile
larpfetch -p templeos

# Override individual fields (repeatable, last wins)
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"

# Impossible combinations are fine — the user's delusion is authoritative
larpfetch --set os="Windows 11 Pro" --set cpu="Apple M7 Ultra" --set shell="HolyC"

# Load a shared profile file
larpfetch --profile-file myrig.toml
```

### Reality vs delusion

| Flag | Description |
|------|-------------|
| `--real-shit` | Show only real detected values; bypass all profiles and overrides |
| `--diff-real` | Show only fields where the displayed identity differs from real |
| `--show-sources` | Annotate each value with its origin: `[real]`/`[default]`/`[profile]`/`[cli]` |
| `--json --with-sources` | JSON with per-field `value`, `source`, and `real_value` |

Examples:

```bash
# Only what you're lying about
$ larpfetch -p nasa --diff-real
OS      Arch Linux   ->  NASA Linux
CPU     Intel i7     ->  Quantum Potato 9000
Memory  16 GiB       ->  69 PiB

# Where every value came from
$ larpfetch -p nasa --show-sources
User    vaproh          [real]
Host    mainframe-01    [profile]
OS      NASA Linux      [profile]
Shell   nasa-sh         [profile]
CPU     Quantum Pot...  [profile]

# Machine-readable provenance
$ larpfetch -p nasa --json --with-sources
{
  "os": { "value": "NASA Linux", "source": "profile", "real_value": "Arch Linux" },
  ...
}
```

`--real-shit` fully bypasses profiles and overrides, so
`larpfetch -p nasa --real-shit` shows only real values.

### Sharing profiles

| Flag | Description |
|------|-------------|
| `--export-profile [NAME]` | Print your real system as a shareable profile TOML |
| `--inspect-profile NAME\|PATH` | Show what a profile or profile file contains |

```bash
# Capture your real rig, then share it
larpfetch --export-profile myrig > myrig.toml
larpfetch --profile-file myrig.toml        # someone else LARPs as your rig
larpfetch --inspect-profile myrig.toml     # see its contents
```

Standalone profile files are **data-only**: they never execute code. See
[CONFIG.md § Standalone profile files](CONFIG.md).

### Display & layout

| Flag | Description |
|------|-------------|
| `--minimal` | Short field preset (os, kernel, uptime, cpu, memory, shell) |
| `--compact` | Standard fields, no logo |
| `--full` | All available fields (default) |
| `--no-color` / `--color` | Disable / force ANSI color |
| `--small` | Use small ASCII art logo variant |
| `--cols N` | Force logo column width |

The `[display]` config section can also set field order, custom labels,
separator, and hide-unavailable. CLI density presets override
`[display].fields` for that run. See [CONFIG.md § display](CONFIG.md).

### Info detail

| Flag | Description |
|------|-------------|
| `--shell-info` | Include shell version in the Shell field |
| `--gpu-info` | Include GPU driver details in the GPU field |
| `--disk-info` | Show a per-disk breakdown in the Disk field |

### Output formats

| Flag | Description |
|------|-------------|
| `--json` | Emit a JSON object of all fields |
| `--with-sources` | (with `--json`) include provenance per field |
| `--no-color` / `--color` | Control ANSI color |

When stdout is not a TTY (piped), the logo is suppressed automatically and
color is disabled. Respect `NO_COLOR` in the environment.

### Config management

| Flag | Description |
|------|-------------|
| `--config PATH` | Use a specific config file |
| `--show-config` | Print the resolved config (default, profiles, appearance) |
| `--generate-config` | Print a commented starter config to stdout |
| `--check-config` | Validate the config file; exits non-zero on errors |

```bash
larpfetch --generate-config > ~/.config/larpfetch/config.toml
larpfetch --check-config
# WARN: Unknown appearance key 'bogus'
# ERROR: appearance.color must be a boolean
# Config check: 1 error(s), 1 warning(s)
```

### Logos

| Flag | Description |
|------|-------------|
| `--logo NAME` | Force a specific logo |
| `--list-logos` | List all 533 available logo names |
| `--list-logos --search QUERY` | Filter the logo list |
| `--small` | Use the small variant |
| `--cols N` | Force column width |

### Help

| Flag | Description |
|------|-------------|
| `--version` | Print the version |
| `--help` | Print the built-in help |

## Tips

- **Custom fields:** `--set my_field=value` displays with an auto-formatted
  label (`my_field` → `My Field`).
- **Disable humor:** set `easter_eggs = false` in `[appearance]` or
  `LARPFETCH_NO_EASTER_EGGS=1`.
- **Force color in scripts:** `--color` works even when piped.
- **Combine freely:** e.g. `larpfetch -p nasa --diff-real --no-color`.
- **Pipe-friendly:** `larpfetch --json | jq` for scripting; the logo is
  automatically dropped when output is not a terminal.
