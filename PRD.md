# larpfetch Product Requirements Document

## 1. Product summary

**larpfetch** is a cross-platform, meme-first terminal system-information tool inspired by fetch utilities. It detects real system information, but its defining feature is allowing users to LARP as any operating system, distro, kernel, hardware configuration, hostname, shell, desktop environment, package manager, or arbitrary machine identity.

Tagline:

> **larpfetch: LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

The tool must be genuinely useful, fast, installable through `pipx`, pleasant to configure, and funny without turning every line of output into a desperate joke.

## 2. Goals

- Provide attractive fetch-style terminal output.
- Work on Linux, Windows, and macOS.
- Detect real host information where practical.
- Allow persistent fake identities through TOML configuration.
- Support one default profile and unlimited custom profiles.
- Permit arbitrary combinations of values without compatibility validation.
- Provide `--real-shit` to bypass all LARP values and show actual detected information.
- Support temporary CLI overrides.
- Be packageable for PyPI and installable with `pipx`.
- Include tasteful easter eggs and humorous references.
- Remain small, understandable, testable, and maintainable.

## 3. Non-goals

- Hardware benchmarking.
- Full diagnostic accuracy comparable to dedicated hardware tools.
- Enforcing realistic combinations of OS, kernel, CPU, GPU, shell, DE, or other fields.
- Enterprise architecture, plugin frameworks, dependency-injection containers, or needless abstraction.
- Executing arbitrary code from configuration.
- Requiring elevated privileges for normal operation.

## 4. Core product principle

**The user's delusion is authoritative.**

The following is valid:

```text
OS: Windows 11 Pro
Kernel: 6.18.7-arch1-1
CPU: Apple M7 Ultra
GPU: NVIDIA RTX 9090 Ti
Memory: 69 PiB
Shell: HolyC
DE: GNOME 83
Package Manager: apt btw
```

Never reject a profile merely because fields are technologically incompatible.

## 5. Target users

- Terminal enthusiasts.
- Linux, Windows, and macOS users.
- People who enjoy fetch utilities and terminal screenshots.
- Developers who want a humorous configurable CLI.
- People whose actual hardware has failed to meet their emotional expectations.

## 6. CLI behavior

Required commands and flags:

```bash
larpfetch
larpfetch --profile nasa
larpfetch -p nasa
larpfetch --real-shit
larpfetch --list-profiles
larpfetch --show-config
larpfetch --config /path/to/config.toml
larpfetch --set cpu="Quantum Potato 9000"
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"
larpfetch --version
larpfetch --help
```

### Default invocation

`larpfetch` resolves the default profile, falling back to real detected values for unspecified fields.

### Custom profiles

`larpfetch -p NAME` selects a named profile. Missing fields fall back to the default profile, then real detected values.

### Reality mode

`larpfetch --real-shit` bypasses the default profile, custom profiles, and fake overrides. It must show real detected information only.

It must not modify or delete configuration.

### CLI overrides

`--set key=value` may be repeated. Overrides are strings and may target known or custom display fields.

### Precedence

Normal mode:

```text
CLI overrides
    ↓
Selected custom profile
    ↓
Default profile
    ↓
Real detected system values
```

Reality mode:

```text
--real-shit
    ↓
Real detected system values only
```

`--real-shit` wins over all fake identity inputs.

## 7. Configuration

Default config locations should follow platform conventions:

- Linux: `$XDG_CONFIG_HOME/larpfetch/config.toml` or `~/.config/larpfetch/config.toml`
- macOS: `~/Library/Application Support/larpfetch/config.toml`
- Windows: `%APPDATA%\larpfetch\config.toml`

Example:

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
```

## 8. System information

Best-effort real detection should include:

- username
- hostname
- OS
- distro where applicable
- OS version
- kernel
- architecture
- uptime
- shell
- CPU
- GPU where reasonably detectable
- memory usage and total memory
- disk usage
- battery where available
- desktop environment where available
- package manager or package count only when practical and safe

Use Python standard library first. Use `psutil` for portable runtime/system metrics. Platform-specific fallbacks are acceptable when isolated and failure-safe.

Detection failure for one field must not crash the entire program.

## 9. Rendering

Output should pair an ASCII logo with aligned information.

Requirements:

- ANSI colors when supported.
- Respect `NO_COLOR`.
- Disable color when output is not a TTY unless explicitly forced.
- Correct alignment when ANSI escape sequences are present.
- Graceful handling of narrow terminals.
- Built-in logos for at least:
  - generic
  - Linux
  - Arch Linux
  - Ubuntu
  - Debian
  - Fedora
  - Windows
  - macOS
  - TempleOS, if legally and practically appropriate as original ASCII artwork
- Unknown identities use a generic logo.
- Logo selection should follow displayed/LARP identity, not actual host OS, unless `--real-shit` is active.

## 10. Real versus LARP distinction

The output should contain a subtle optional distinction between real and LARP modes.

Possible implementation:

LARP mode:

```text
Authenticity: 3%
```

Reality mode:

```text
Authenticity: 100%
Disappointment: immeasurable
```

Do not hard-code excessive jokes into every invocation. Humor should be restrained and discoverable.

## 11. Easter eggs

Include a small, documented-in-code but not loudly advertised easter-egg system.

Rules:

- No network calls.
- No offensive or hateful material.
- No destructive behavior.
- No misleading security claims.
- Rare jokes may appear based on specific profile values or combinations.
- Tests must make randomness deterministic.
- Provide a way to disable easter eggs through config or environment variable.

Suggested references:

- `Source: trust me bro`
- `Reality Leakage: 100.00%`
- `The allegations were true.`
- `Reality has out-LARPed the LARP.` when real hardware is absurdly powerful, using conservative and clearly documented thresholds.

## 12. Packaging

- Python 3.11+.
- `pyproject.toml`.
- `src/` layout.
- Console entry point named `larpfetch`.
- Runtime dependency: preferably only `psutil`, plus standard library.
- TOML reading should use `tomllib`.
- Development dependencies may include `pytest`, `pytest-cov`, `ruff`, and type-checking tools if useful.
- Must support:
  - `pip install .`
  - `pipx install .`
  - eventual PyPI publication

## 13. Quality requirements

- Unit tests for config resolution and precedence.
- Unit tests proving `--real-shit` bypasses every LARP layer.
- Unit tests for malformed config.
- Unit tests for unknown fields.
- Unit tests for ANSI-safe alignment.
- Platform collectors must be mockable.
- CLI smoke tests.
- No shell command may be built through unsafe string interpolation.
- Subprocess calls require timeouts and argument arrays, never `shell=True` without an exceptional documented reason.
- A single failed platform probe must degrade gracefully.

## 14. Suggested package structure

```text
larpfetch/
├── pyproject.toml
├── README.md
├── LICENSE
├── AGENTS.md
├── PRD.md
├── IMPLEMENTATION.md
├── PROMPT.md
├── src/
│   └── larpfetch/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── resolver.py
│       ├── renderer.py
│       ├── easter_eggs.py
│       ├── logos.py
│       └── collectors/
│           ├── __init__.py
│           ├── common.py
│           ├── linux.py
│           ├── windows.py
│           └── macos.py
└── tests/
```

Keep this structure flexible. Do not create files merely to satisfy a diagram if simpler code is clearer.

## 15. Acceptance criteria

The project is complete when:

1. `pipx install .` installs a working `larpfetch` command.
2. `larpfetch` works on supported platforms with graceful degradation.
3. A default profile can override real information.
4. Custom profiles can be selected with `-p/--profile`.
5. Arbitrary impossible combinations are accepted.
6. `--set key=value` temporarily overrides displayed values.
7. `--real-shit` displays only real detected values.
8. Linux, Windows, and macOS are supported.
9. Displayed identity controls logo selection.
10. Tests cover precedence and reality-mode invariants.
11. The README includes examples, installation, config docs, screenshots/placeholders, humor, and limitations.
12. The package is ready for PyPI publication after name availability and metadata are verified.
