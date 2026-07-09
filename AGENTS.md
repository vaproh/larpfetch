# AGENTS.md

## Mission

Build and maintain **larpfetch**, a cross-platform terminal fetch utility that detects real system information and allows users to LARP as arbitrary machines through persistent profiles and CLI overrides.

The product is humorous. The implementation must not be a joke.

## Sacred product rule

**The user's delusion is authoritative.**

Never validate whether identity fields make technological sense together. This is valid:

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

Do not "correct" it.

## Required invariant

`--real-shit` must bypass every source of LARP data.

When `--real-shit` is active:

- Ignore default profile values.
- Ignore selected custom profiles.
- Ignore fake CLI `--set` overrides.
- Show only best-effort real detected system data.
- Do not modify configuration.
- Do not delete profiles.
- Do not silently mix fake fallback values into real output.

This invariant requires explicit automated tests.

## Engineering principles

1. Prefer simple code over clever architecture.
2. Use the standard library where reasonable.
3. Use `psutil` for portable system metrics.
4. Keep platform-specific detection isolated.
5. A failed detector must return an unavailable value, not crash the app.
6. Avoid abstract base classes unless multiple implementations genuinely need a shared contract.
7. Do not create factories for factories.
8. Do not add a plugin system in v1.
9. Do not add network calls.
10. Do not use AI-generated filler comments or giant docstrings that merely restate code.
11. Do not claim support that is not tested or gracefully implemented.
12. Keep startup fast.

## Data model

Use a normalized representation for system/display information. Known fields may include:

- username
- hostname
- os
- distro
- os_version
- kernel
- architecture
- uptime
- shell
- cpu
- gpu
- memory
- disk
- battery
- de
- package_manager
- package_count

Support arbitrary additional string fields from profiles and `--set`.

Known fields should have stable display ordering. Custom fields should follow deterministically.

## Resolution algorithm

Normal mode:

```text
real detected values
    ← overridden by default profile
    ← overridden by selected custom profile
    ← overridden by CLI --set values
```

Equivalent precedence:

```text
CLI overrides > selected custom profile > default profile > real values
```

Reality mode:

```text
--real-shit > everything else
```

Do not accidentally implement custom profiles as total replacements. Missing fields should inherit from the default profile, then real values.

## Configuration

Use TOML and `tomllib`.

Expected sections:

```toml
[default]

[profiles.NAME]

[appearance]
```

Requirements:

- Helpful errors for invalid TOML.
- Helpful error when requested profile does not exist.
- Unknown profile fields are allowed.
- Values intended for display should be normalized to strings.
- Never execute values from config.
- Respect explicit `--config PATH`.

## CLI

Required surface:

```text
larpfetch
larpfetch -p NAME
larpfetch --profile NAME
larpfetch --real-shit
larpfetch --list-profiles
larpfetch --show-config
larpfetch --config PATH
larpfetch --set key=value
larpfetch --version
larpfetch --help
```

`--set` must be repeatable.

Prefer `argparse` unless another dependency provides clear value. Avoid dependency inflation for cosmetic convenience.

## Cross-platform behavior

Support Linux, Windows, and macOS.

Collectors:

- Common collector: username, hostname, architecture, uptime, memory, disk, battery where portable.
- Linux collector: distro from `/etc/os-release`, kernel, shell, DE, GPU best effort.
- Windows collector: Windows edition/version/build, kernel/version, shell, GPU best effort.
- macOS collector: macOS product version, Darwin kernel, shell, GPU best effort.

Rules:

- Avoid requiring root/admin.
- Use subprocess argument arrays.
- Use timeouts.
- Never use `shell=True` unless absolutely necessary and documented.
- Catch missing-command and timeout errors.
- Do not let optional probes crash startup.

## Rendering

- Pair ASCII logo and aligned key/value rows.
- Select logo from displayed identity.
- In `--real-shit`, select from real identity.
- Respect `NO_COLOR`.
- Avoid broken alignment caused by ANSI codes.
- Handle Unicode carefully.
- Unknown distro/OS gets generic logo.
- Keep original ASCII artwork in-repo. Do not copy copyrighted ASCII art blindly from third-party projects.

## Humor

The humor should be dry and sparse.

Good:

```text
Authenticity: 3%
Source: trust me bro
Reality Leakage: 100.00%
```

Bad:

- A joke on every line.
- Random meme spam that obscures system information.
- Offensive jokes.
- Humor that makes tests flaky.
- Pretending fake values are security facts.

Easter eggs must be deterministic under test and disableable.

## Testing requirements

At minimum, test:

- no config
- default profile
- selected custom profile
- custom profile inheritance
- CLI overrides
- arbitrary unknown fields
- impossible field combinations accepted
- missing profile error
- malformed TOML error
- `--real-shit` ignores default profile
- `--real-shit` ignores selected profile
- `--real-shit` ignores CLI fake overrides
- collector failure degradation
- logo selection by displayed identity
- real logo selection in reality mode
- ANSI-safe alignment
- `NO_COLOR`
- CLI help/version
- installable console entry point where practical

Mock platform-specific system calls in unit tests.

## Security

- No `eval` or `exec`.
- No arbitrary code execution from TOML.
- No network access.
- No unsafe shell interpolation.
- No secrets collection.
- Do not expose environment variables beyond explicitly needed values such as shell, config paths, desktop session, and color conventions.
- Do not persist real system information unless a future feature explicitly requires it and documents it.

## Packaging

Use:

- Python 3.11+
- `pyproject.toml`
- `src/` layout
- console script `larpfetch`
- `psutil`
- `tomllib`

Recommended dev tooling:

- pytest
- pytest-cov
- ruff

Keep runtime dependencies minimal.

## Workflow for coding agents

Before editing:

1. Read `PRD.md`.
2. Read this file.
3. Read `IMPLEMENTATION.md`.
4. Inspect existing code and tests.
5. State a brief implementation plan internally, then execute.

During implementation:

1. Work in small coherent changes.
2. Run focused tests after each subsystem.
3. Run the full suite before completion.
4. Run linting.
5. Test the CLI manually.
6. Verify packaging metadata.
7. Do not leave placeholders, TODO implementations, fake test passes, or commented-out broken code.

Before declaring completion:

- Ensure acceptance criteria in `PRD.md` are met.
- Ensure `--real-shit` invariant is covered by tests.
- Ensure the project installs locally.
- Ensure README commands match actual behavior.
- Ensure no generated artifacts or secrets are accidentally committed.

## Final warning

Do not overengineer this.

It is a fetch tool that lies.
