# AGENTS.md

Guidance for agents working on **larpfetch**. Follow the project conventions and the roadmap; keep changes small and tested.

## Mission

Build and maintain **larpfetch**, a cross-platform terminal fetch utility that detects real system information and lets users LARP as arbitrary machines through persistent profiles and CLI overrides.

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
- Ignore selected custom profiles (and `--profile-file`).
- Ignore fake CLI `--set` overrides.
- Show only best-effort real detected system data.
- Do not modify configuration.
- Do not delete profiles.
- Do not silently mix fake fallback values into real output.

This invariant requires explicit automated tests (see `tests/test_integration.py` and `tests/test_resolver.py`).

## Engineering principles

1. Prefer simple code over clever architecture.
2. Use the standard library where reasonable.
3. Use `psutil` for portable system metrics.
4. Keep platform-specific detection isolated.
5. A failed detector must return an unavailable value, not crash the app.
6. Avoid abstract base classes unless multiple implementations genuinely need a shared contract.
7. Do not create factories for factories.
8. Do not add a plugin system yet — shareable TOML profiles are enough.
9. Do not add network calls.
10. Do not use AI-generated filler comments or giant docstrings that merely restate code.
11. Do not claim support that is not tested or gracefully implemented.
12. Keep startup fast.

## Code layout

`src/larpfetch/` (installed as the `larpfetch` package):

- `models.py` — `SystemInfo` (OrderedDict of fields), `KNOWN_FIELDS`, `FIELD_LABELS`, `FIELD_ALIASES`, `META_FIELDS` (`logo`), `DisplayConfig`, `DENSITY_PRESETS`.
- `collectors/` — platform probes. `common.collect_all(...)` returns a `SystemInfo` of real values. Common fields plus Linux/Windows/macOS specifics.
- `resolver.py` — `resolve()` merges layers; `resolve_with_sources()` also returns provenance (`real`/`default`/`profile`/`cli`).
- `config.py` — TOML loading via `tomllib`: `load_config`, profile/default/appearance/display extractors, `load_profile_file`, `export_profile_toml`, `validate_config`.
- `profiles.py` — built-in profiles (`get_builtin_profiles`).
- `renderer.py` — `render()`, `render_diff()`, `render_sources()`. Logo/color handling.
- `cli.py` — `build_parser()`, `main()`. Parses flags, wires everything together.
- `logos.py` — 533 fastfetch logos + color placeholders.
- `easter_eggs.py` — deterministic, disableable humor.

`tests/` mirrors this layout one file per module.

## Conventions

- Python 3.11+, `src/` layout, `pyproject.toml` + `uv`.
- Type hints everywhere; return/accept `SystemInfo` or `dict[str, str]`.
- Line length 99; `ruff` lint must stay clean (`just lint`).
- Runtime dependency is `psutil` only. Dev: `pytest`, `ruff`.
- Run tasks with `just`: `just check` (lint + test), `just test`, `just lint`, `just fmt`.

## Data model

`SystemInfo.fields` is an `OrderedDict[str, str]`. Known fields (stable display order):

- username, hostname, os, distro, os_version, kernel, architecture
- uptime, shell, cpu, gpu, memory, disk, disk_detail, battery
- de, package_manager, package_count

Support arbitrary additional string fields from profiles and `--set` (custom fields display after known ones).

- `FIELD_LABELS` — display label per known field.
- `FIELD_ALIASES` — config/CLI aliases (`host`, `ram`, `arch`, `packages`, `pkgs`).
- `META_FIELDS` — non-display fields (`logo`).
- `DisplayConfig` — controls `[display]`: `fields` order, `field_labels`, `separator`, `hide_unavailable`.
- `display_entries()` returns `(key, label, value)` triples (powers diff/sources).

## Resolution algorithm

Normal mode: `CLI overrides > selected custom profile > default profile > real values`

Reality mode: `--real-shit > everything else`

Custom profiles are not total replacements — missing fields inherit from the default profile, then real values. `resolve_with_sources()` tracks each field's origin; `--show-sources`, `--diff-real`, and `--json --with-sources` consume it.

## Configuration

TOML via `tomllib`. Sections: `[default]`, `[profiles.NAME]`, `[appearance]`, `[display]`.

- `Profiles` set any field plus optional `logo` (built-in name or inline ASCII art).
- `[display]` controls field order, labels, separator, hide-unavailable.
- Standalone profile files (`--profile-file PATH`) are data-only: scalar key/value pairs (flat or under `[profile]`), never executed. `--export-profile` writes this format; `--check-config` validates the main config.

Full reference: `docs/CONFIG.md`.

## CLI

Surface (all flags repeatable where noted):

- Identity: `-p/--profile NAME`, `--profile-file PATH`, `--distro NAME`, `--logo NAME`, `--set key=value` (repeatable), `--real-shit`
- Output modes: `--json`, `--with-sources`, `--diff-real`, `--show-sources`, `--minimal`, `--compact`, `--full`, `--no-color`/`--color`, `--small`, `--cols N`, `--generate-config`
- Info detail: `--shell-info`, `--gpu-info`, `--disk-info`
- Profiles/config: `--list-profiles`, `--show-config`, `--inspect-profile NAME|PATH`, `--check-config`, `--config PATH`, `--list-logos [--search QUERY]`, `--version`, `--help`

`--set` must be repeatable.

## Cross-platform

Linux, Windows, macOS. Collectors: common (username, hostname, arch, uptime, memory, disk, battery), Linux (os-release, kernel, shell, DE, GPU), Windows (edition/version, kernel, shell, GPU), macOS (product version, Darwin, shell, GPU).

Rules: no root required, argument arrays for subprocess, timeouts, never `shell=True`, catch failures gracefully.

## Rendering

- Pair ASCII logo and aligned key/value rows.
- 533 logos from fastfetch (MIT) with ANSI color support ($1/$2/$3 placeholders).
- Logo selection follows displayed identity (or real identity in `--real-shit`).
- Profiles can override logos by name or provide custom art.
- Respect `NO_COLOR`. Avoid broken alignment from ANSI codes (count visible width, not ANSI length).
- Keep original ASCII artwork in-repo.

## Humor

Dry and sparse. Easter eggs must be deterministic under test and disableable (`[appearance] easter_eggs = false` or `LARPFETCH_NO_EASTER_EGGS=1`). No offensive material.

## Testing

At minimum cover: config loading, display layout config, profile resolution, `--real-shit` invariant (ignores all fake inputs), CLI parsing, logo selection, ANSI alignment, `NO_COLOR`, collector degradation, easter egg determinism, installable entry point.

Mock platform-specific system calls in unit tests. `just check` must pass (currently 300+ tests).

## Security

No `eval`/`exec`, no arbitrary code execution from TOML, no network access, no unsafe shell interpolation, no secrets collection. Standalone profiles are data-only.

## Common patterns

**Add a new display field:** add to `KNOWN_FIELDS` (models.py) → `FIELD_LABELS` → the relevant collector in `collectors/` → a renderer/label test. Custom fields need no constant.

**Add a new CLI flag:** add the `add_argument` in `build_parser()` (cli.py) → wire it in `main()` → add a parser test in `tests/test_cli.py` and a behavior test in `tests/test_integration.py`.

**Add a new built-in profile:** add an entry in `profiles.BUILTIN_PROFILES`.

## Workflow

1. Read `PRD.md`, `AGENTS.md`, and `ROADMAP.md`.
2. Inspect existing code and tests.
3. Work in small coherent changes following the roadmap.
4. Update relevant files for every change — not just code:
   - Add/extend tests (`tests/`) so `just check` covers the new behavior.
   - Update `CHANGELOG.md` (new `## vX.Y.Z` entry describing the change).
   - Update user-facing docs that the change affects: `README.md`, `docs/CONFIG.md`, `ROADMAP.md` (mark shipped items), and `AGENTS.md`/`PRD.md` when conventions or the feature surface change.
   - Bump `version` in `pyproject.toml` and `src/larpfetch/__init__.py` when cutting a release; refresh `uv.lock` if `pyproject.toml` changed (`uv lock`).
5. Run `just check` after each change.
6. Test the CLI manually (`uv run larpfetch ...`).
7. Commit after every feature addition or change.
8. Do not leave placeholders, TODOs, or broken code.

## Publishing

```bash
# 1. Commit the release work, then tag and push
git tag vX.Y.Z && git push origin main && git push origin vX.Y.Z

# 2. Load PyPI token from .env and publish to PyPI
export $(grep -v '^#' .env | xargs) && just publish

# 3. Publish the GitHub release for the same tag
just gh-release

# Or do all three steps in one:
just release

# Dry run of the PyPI publish:
export $(grep -v '^#' .env | xargs) && just publish-dry
```

`just gh-release` and `just release` read the version from `pyproject.toml` and
build the GitHub release title/notes from `CHANGELOG.md` automatically (the
first line under each `## vX.Y.Z` heading is the title summary; the rest
is the notes body).

The GitHub release title and notes should summarize the new features for that version. Do not overengineer this. It is a fetch tool that lies.

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
