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

Use a normalized representation for system/display information. Known fields:

- username, hostname, os, distro, os_version, kernel, architecture
- uptime, shell, cpu, gpu, memory, disk, disk_detail, battery
- de, package_manager, package_count

Support arbitrary additional string fields from profiles and `--set`.

Known fields have stable display ordering. Custom fields follow deterministically.

## Resolution algorithm

Normal mode: `CLI overrides > selected custom profile > default profile > real values`

Reality mode: `--real-shit > everything else`

Do not accidentally implement custom profiles as total replacements. Missing fields inherit from the default profile, then real values.

## Configuration

Use TOML and `tomllib`. Expected sections: `[default]`, `[profiles.NAME]`, `[appearance]`.

Profiles can include a `logo` field to reference a built-in logo by name or provide inline custom ASCII art.

Full config reference: `docs/CONFIG.md`.

## CLI

Required surface: `larpfetch`, `-p NAME`, `--profile NAME`, `--real-shit`, `--list-profiles`, `--show-config`, `--config PATH`, `--set key=value`, `--json`, `--shell-info`, `--gpu-info`, `--disk-info`, `--version`, `--help`.

`--set` must be repeatable.

## Cross-platform

Support Linux, Windows, and macOS. Collectors: common (username, hostname, arch, uptime, memory, disk, battery), Linux (os-release, kernel, shell, DE, GPU), Windows (edition/version, kernel, shell, GPU), macOS (product version, Darwin, shell, GPU).

Rules: no root required, argument arrays for subprocess, timeouts, never `shell=True`, catch failures gracefully.

## Rendering

- Pair ASCII logo and aligned key/value rows.
- 533 logos from fastfetch (MIT) with ANSI color support ($1/$2/$3 placeholders).
- Logo selection follows displayed identity (or real identity in `--real-shit`).
- Profiles can override logos by name or provide custom art.
- Respect `NO_COLOR`. Avoid broken alignment from ANSI codes.
- Keep original ASCII artwork in-repo.

## Humor

Dry and sparse. Easter eggs must be deterministic under test and disableable.

## Testing

At minimum: config loading, profile resolution, `--real-shit` invariant (ignores all fake inputs), CLI parsing, logo selection, ANSI alignment, `NO_COLOR`, collector degradation, easter egg determinism, installable entry point.

Mock platform-specific system calls in unit tests.

## Security

No `eval`/`exec`, no arbitrary code execution from TOML, no network access, no unsafe shell interpolation, no secrets collection.

## Packaging

Python 3.11+, `pyproject.toml`, `src/` layout, console script `larpfetch`, runtime deps: `psutil` only. Dev deps: `pytest`, `ruff`. Use `uv` for dependency management. Run tasks via `just`.

## Workflow

1. Read `PRD.md` and this file.
2. Inspect existing code and tests.
3. Work in small coherent changes.
4. Run `just check` after each change.
5. Test the CLI manually.
6. Do not leave placeholders, TODOs, or broken code.

Do not overengineer this. It is a fetch tool that lies.

## Demo GIF generation

Record with asciinema, render with agg:

```bash
# 1. Write demo runner script
cat > /tmp/demo_runner.sh << 'SCRIPT'
#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
_type() {
  local s="$1"
  for ((i=0; i<${#s}; i++)); do printf '\033[1;33m%s\033[0m' "${s:$i:1}"; sleep 0.03; done
}
_clear() { printf '\033[2J\033[H'; }
_clear; sleep 0.5
printf '\033[1;36mλ\033[0m › '; _type "larpfetch"; echo; sleep 0.3; larpfetch; sleep 3
_clear; printf '\033[1;36mλ\033[0m › '; _type "larpfetch -p templeos"; echo; sleep 0.3; larpfetch -p templeos; sleep 3
_clear; printf '\033[1;36mλ\033[0m › '; _type "larpfetch --json"; echo; sleep 0.3; larpfetch --json; sleep 2; echo
SCRIPT
chmod +x /tmp/demo_runner.sh

# 2. Record
rm -f /tmp/larpfetch_demo.cast
asciinema rec /tmp/larpfetch_demo.cast \
  --command "stty cols 95 rows 24 && /tmp/demo_runner.sh" \
  --overwrite

# 3. Fix header dimensions
python3 -c "
import json
with open('/tmp/larpfetch_demo.cast') as f:
    h = json.loads(f.readline()); d = f.read()
h['term']['cols'] = 95; h['term']['rows'] = 24
with open('/tmp/larpfetch_demo.cast', 'w') as f:
    f.write(json.dumps(h, separators=(',', ':')) + '\n' + d)
"

# 4. Download agg if needed
which agg || curl -sL https://github.com/asciinema/agg/releases/latest/download/agg-x86_64-unknown-linux-gnu -o /tmp/agg && chmod +x /tmp/agg
AGG=/tmp/agg

# 5. Render GIF
$AGG --theme github-dark --cols 95 --rows 24 --font-size 14 --speed 1 \
  /tmp/larpfetch_demo.cast assets/demo.gif
```
