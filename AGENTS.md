# AGENTS.md

Operating manual for autonomous coding agents working on **larpfetch**. Follow it exactly. This repository is 100% made by autonomous agents — no human coding or review is expected.

## Mission

Build and maintain **larpfetch**, a cross-platform terminal fetch utility that detects real system information and lets users LARP as arbitrary machines through persistent profiles, shareable profile files, and CLI overrides.

The product is humorous. The implementation must not be a joke.

## Sacred product rule

**The user's delusion is authoritative.** Never validate whether identity fields make technological sense together. This is valid:

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

When `--real-shit` is active: ignore default profile, selected profile, `--profile-file`, and CLI `--set` overrides; show only best-effort real detected system data; do not modify or delete config/profiles; do not mix fake fallback values into real output. This invariant requires explicit automated tests (see `tests/test_integration.py`, `tests/test_resolver.py`).

## Engineering principles

1. Prefer simple code over clever architecture.
2. Use the standard library where reasonable.
3. Use `psutil` for portable metrics; it is the only runtime dependency.
4. Keep platform-specific detection isolated and failing gracefully.
5. A failed detector returns an unavailable value; it never crashes the app.
6. Avoid abstract base classes unless multiple implementations genuinely need a shared contract.
7. Do not create factories for factories.
8. Do not add a plugin system yet — shareable TOML profiles are enough.
9. Do not add network calls, ever.
10. No AI-generated filler comments or docstrings that restate code.
11. Do not claim support that is not tested or gracefully implemented.
12. Keep startup fast.

## Autonomous operation

- You have full authority to implement roadmap items, run the test/lint gate, commit, tag, push, and publish releases. **Do not block on human approval.**
- If a decision is ambiguous, make a reasonable, documented choice and continue.
- Tooling available: `uv` (deps/tests), `just` (tasks), `gh` (GitHub releases), `.env` (PyPI token consumed by `just publish`).
- The quality gate is `just check` (ruff lint + pytest). It must be green before you commit or release.
- Never leave the repo in a broken or half-wired state.

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

`tests/` mirrors this layout one file per module. See `docs/architecture.md` for the data-flow diagram, resolution algorithm, and security model. Full config reference: `docs/CONFIG.md`. Full command reference: `docs/USAGE.md`.

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

## Picking up a roadmap item

1. Read `ROADMAP.md`; pick the next item under the current theme that is **not** marked ✅.
2. Keep the change scoped to that item. Do not refactor unrelated code.
3. Implement in the correct module (new detector → `collectors/`; resolver/display change → `resolver.py`/`renderer.py`; config → `config.py`; flag → `cli.py`). Reuse existing helpers; add a new module only if justified.
4. If the item needs platform-specific probes, isolate them and degrade gracefully (return unavailable, never raise).

## Definition of Done (per feature)

- [ ] Behavior implemented in the correct module.
- [ ] `--real-shit` invariant preserved; add/adjust a test if the feature touches resolution.
- [ ] Tests added in the matching `tests/<module>.py`; full `just check` is green.
- [ ] `CHANGELOG.md` updated: add a bullet under `## Unreleased` describing the feature.
- [ ] `ROADMAP.md` updated: mark the item ✅ (and the theme "Shipped" when all its items are ✅).
- [ ] Relevant user docs updated only where the change affects them: `README.md`, `docs/USAGE.md`, `docs/CONFIG.md`, `docs/architecture.md`, `AGENTS.md`, `PRD.md`.
- [ ] No placeholders, TODOs, dead code, or stray `print()` left in `src/`.

## Versioning & release policy

- A ROADMAP theme (e.g. v1.5) ships as **one minor version** `vX.Y.0`.
- Implement theme items into `## Unreleased`. **Do not** bump the version or release until the theme is complete (or a deliberate, documented subset).
- To cut a release:
  1. Move the `## Unreleased` bullets under a new `## vX.Y.0` heading whose first line is a one-line summary; the rest is the notes body (consumed by `just release`).
  2. Bump `version` in `pyproject.toml` and `src/larpfetch/__init__.py`; run `uv lock` (refresh `uv.lock` if `pyproject.toml` changed).
  3. Mark the ROADMAP theme "Shipped" (e.g. `## v1.5 — … — Shipped`).
  4. `git commit` with message `feat: vX.Y <theme summary>`, then run `just release`.
- `just release` tags `vX.Y.0`, pushes, publishes to PyPI, and creates the GitHub release (title/notes auto-built from CHANGELOG). Use `just gh-release` to create only the GitHub release, or `just publish` for PyPI only.
- Patch releases (`vX.Y.Z`) are for fixes/chores between themes: bump patch, update CHANGELOG, then `just release`.
- Dry-run PyPI publish with `just publish-dry` when unsure.

## Common patterns

**Add a new display field:** add to `KNOWN_FIELDS` (models.py) → `FIELD_LABELS` → the relevant collector in `collectors/` → a renderer/label test. Custom fields need no constant.

**Add a new CLI flag:** add the `add_argument` in `build_parser()` (cli.py) → wire it in `main()` → add a parser test in `tests/test_cli.py` and a behavior test in `tests/test_integration.py`.

**Add a new built-in profile:** add an entry in `profiles.BUILTIN_PROFILES`.

**Add a new detector:** put it in `collectors/common.py` (or a platform file), wrap in try/except so failures degrade to an empty value, and add a unit test that mocks the platform call.

## Workflow

1. Read `PRD.md`, `AGENTS.md`, and `ROADMAP.md`.
2. Pick the next unmarked roadmap item; scope tightly.
3. Implement + add tests; run `just check` until green.
4. Update relevant docs (CHANGELOG `## Unreleased`, ROADMAP ✅, plus affected README/USAGE/CONFIG/architecture/AGENTS/PRD).
5. Commit (`feat:`/`fix:`/`docs:`/`chore:` prefix).
6. When a theme is complete, version-bump + `just release` (see policy above).
7. Do not leave placeholders, TODOs, or broken code.

## Publishing

```bash
# Full release (tag + push + PyPI + GitHub release) for the current version:
just release

# Or step by step:
export $(grep -v '^#' .env | xargs) && just publish   # PyPI
just gh-release                                  # GitHub release
```

`just gh-release` and `just release` read the version from `pyproject.toml` and
build the GitHub release title/notes from `CHANGELOG.md` automatically (the
first line under each `## vX.Y.Z` heading is the title summary; the rest
is the notes body).

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
