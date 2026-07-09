# One-shot AI Coding Prompt for larpfetch

Copy the prompt below into a capable coding agent with access to this repository.

---

You are implementing a complete, production-quality open-source Python CLI project named **larpfetch**.

Read these files fully before writing code:

1. `PRD.md`
2. `AGENTS.md`
3. `IMPLEMENTATION.md`

Then inspect the repository and implement the entire project end-to-end.

## Product

`larpfetch` is a cross-platform fetch-style terminal system-information utility with one defining gimmick: users can LARP as any operating system, distro, kernel, hardware configuration, hostname, shell, desktop environment, package manager, or arbitrary machine identity.

Tagline:

> **larpfetch: LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

The humor is important, but the software must be genuinely polished.

## Non-negotiable behavior

Implement:

```bash
larpfetch
larpfetch -p nasa
larpfetch --profile nasa
larpfetch --real-shit
larpfetch --list-profiles
larpfetch --show-config
larpfetch --config /path/to/config.toml
larpfetch --set cpu="Quantum Potato 9000"
larpfetch --set os="Windows 11 Pro" --set kernel="6.18.7-arch1-1"
larpfetch --version
larpfetch --help
```

Normal precedence:

```text
CLI overrides > selected custom profile > default profile > real detected values
```

Reality mode:

```text
--real-shit > everything
```

When `--real-shit` is active, do not mix in any fake default-profile, selected-profile, or CLI-override values. This is a hard invariant and must have explicit tests.

## Sacred rule

**The user's delusion is authoritative.**

Never validate compatibility between fields. This must be accepted:

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

Profiles are display identities, not hardware simulations.

## Technical requirements

- Python 3.11+
- Modern `pyproject.toml`
- `src/` layout
- Console entry point: `larpfetch`
- Cross-platform: Linux, Windows, macOS
- Use `psutil` for portable system metrics
- Use `tomllib` for TOML
- Prefer `argparse` for CLI
- Minimal runtime dependencies
- No network calls
- No unsafe shell interpolation
- External commands must use argument arrays and timeouts
- Optional detector failure must never crash the entire application
- Respect `NO_COLOR`
- Correct terminal alignment despite ANSI escape codes
- Original in-repo ASCII logos; do not blindly copy copyrighted artwork
- Displayed LARP identity chooses the logo
- Real identity chooses the logo under `--real-shit`
- Support arbitrary custom fields
- Support default profile plus unlimited named custom profiles
- Missing custom-profile fields inherit from default profile, then real values

## Config example

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

## Humor requirements

Keep humor dry, sparse, and discoverable. Do not spam jokes on every line.

Examples of acceptable optional lines:

```text
Authenticity: 3%
Source: trust me bro
Reality Leakage: 100.00%
The allegations were true.
Reality has out-LARPed the LARP.
```

Include a small easter-egg mechanism that is deterministic under test and can be disabled.

Do not make offensive jokes. Do not obscure useful output.

## Required testing

Use pytest. Include tests for at least:

- no config
- default profile
- selected custom profile
- profile inheritance
- CLI overrides
- repeated `--set`
- arbitrary custom fields
- impossible combinations accepted
- missing profile errors
- malformed TOML
- `--real-shit` ignores default profile
- `--real-shit` ignores selected custom profile
- `--real-shit` ignores fake CLI overrides
- collector failures degrade gracefully
- displayed identity controls logo
- real identity controls logo under `--real-shit`
- ANSI-safe alignment
- `NO_COLOR`
- help/version
- easter eggs are deterministic and disableable

Mock platform-specific facilities where appropriate.

## README

Write a polished README containing:

- project name and tagline
- short demo
- installation via `pipx`
- normal usage
- profiles
- configuration
- CLI overrides
- `--real-shit`
- cross-platform support
- easter eggs without spoiling every one
- development setup
- tests
- limitations
- license

Include this line prominently:

> **larpfetch: LARP as any distro, hardware, or machine you want. Because reality is optional until you pass `--real-shit`.**

## Implementation discipline

Do not overengineer this.

Do not create enterprise abstractions, plugin systems, service locators, dependency-injection frameworks, giant inheritance hierarchies, or unnecessary factories.

Keep the code small, typed where useful, readable, testable, and easy for one developer to maintain.

Do not leave placeholders, fake implementations, TODOs for core functionality, commented-out broken code, or tests that pass without testing meaningful behavior.

## Execution plan

1. Read all project instruction documents.
2. Inspect the repository.
3. Build the package skeleton.
4. Implement data models and real system detection.
5. Implement TOML configuration.
6. Implement pure profile resolution.
7. Implement CLI.
8. Implement logos and renderer.
9. Implement restrained humor/easter eggs.
10. Write comprehensive tests.
11. Write README and license.
12. Run tests.
13. Run linting.
14. Build the package.
15. Test local CLI installation if the environment permits.
16. Fix every discovered issue.
17. Review against every acceptance criterion in `PRD.md`.

Do not stop at scaffolding. Deliver the complete working project.

The final result should feel like a real open-source terminal utility whose core philosophical achievement is allowing a Windows 11 machine to claim it runs an Arch kernel on an Apple M7 Ultra with an RTX 9090 Ti and 69 PiB of RAM.

Build it.
