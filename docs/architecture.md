# Architecture

This document describes how larpfetch is structured internally. For user-facing
behavior, see [README.md](../README.md), [docs/CONFIG.md](CONFIG.md),
[docs/USAGE.md](USAGE.md), and [PRD.md](../PRD.md). For the release plan, see [ROADMAP.md](../ROADMAP.md). For how the project is 100% built and shipped by autonomous agents, see [AGENTS.md](../AGENTS.md).

## Module map

`src/larpfetch/`:

| Module | Responsibility |
|--------|----------------|
| `models.py` | `SystemInfo` data class; `KNOWN_FIELDS`, `FIELD_LABELS`, `FIELD_ALIASES`, `META_FIELDS`; `DisplayConfig`; `DENSITY_PRESETS` |
| `collectors/common.py` | `collect_all(...)` — best-effort real detection across platforms |
| `resolver.py` | `resolve()` and `resolve_with_sources()` — merge layers + track provenance |
| `config.py` | TOML loading/validation: `load_config`, `get_*`, `load_profile_file`, `export_profile_toml`, `validate_config` |
| `profiles.py` | `BUILTIN_PROFILES` and accessors |
| `renderer.py` | `render()`, `render_diff()`, `render_sources()` — logo + key/value output, color |
| `cli.py` | `build_parser()`, `main()` — argument parsing and wiring |
| `logos.py` | 533 fastfetch logos + ANSI color placeholders |
| `easter_eggs.py` | deterministic, disableable humor |

`tests/` mirrors this layout (one file per module).

## Data model

`SystemInfo.fields` is an `OrderedDict[str, str]`. Field iteration order is
deterministic and follows `KNOWN_FIELDS` when populated by collectors.

- `KNOWN_FIELDS` — canonical display order.
- `FIELD_LABELS` — human label per known field.
- `FIELD_ALIASES` — config/CLI aliases (`host`→`hostname`, `ram`→`memory`, `arch`→`architecture`, `packages`/`pkgs`→`package_manager`).
- `META_FIELDS` — non-display fields (`logo`).
- `DisplayConfig` — `[display]` settings: `fields` (order), `field_labels`, `separator`, `hide_unavailable`.
- `display_entries()` returns `(key, label, value)` triples; `display_items()` returns `(label, value)` and is built on top of it.

## Data flow

```
collect_all()  ──►  real: SystemInfo
                         │
resolve_with_sources(real, default, selected, cli, real_shit)
                         │
                         ├─► resolved: SystemInfo      (displayed identity)
                         └─► sources: dict[key, origin] (real/default/profile/cli)
                         │
get_display_config(config) + density presets ─► display_config: DisplayConfig
get_appearance(config) + color flags        ─► appearance: dict
                         │
   ┌─────────────────────┼─────────────────────────────┐
   ▼                     ▼                             ▼
render()          render_diff()              render_sources()
(real output)     (--diff-real)               (--show-sources)

--json            → dict(resolved)  (or real when --real-shit)
--json --with-sources → {key: {value, source, real_value}}
```

`--real-shit` short-circuits `resolve_with_sources` to return the real
`SystemInfo` with all origins `real`; profiles and CLI overrides are bypassed.

## Resolution algorithm

Normal mode precedence:

```
CLI overrides > selected profile (or --profile-file) > default profile > real values
```

Each layer only overwrites a field when its value is non-empty. Missing fields
inherit from the layer below (default inherits from real; selected inherits from
default). `resolve_with_sources()` records the topmost layer that set each field.

Reality mode (`--real-shit`):

```
real values only
```

## Rendering

- `render()` pairs the ASCII logo with aligned `label<sep> value` rows.
- Logo selection: `--logo` > profile `logo` > real OS (when `--real-shit`) >
  displayed OS. A `logo` value matching a built-in name is used directly;
  otherwise it is treated as inline ASCII art.
- Terminal-width awareness: on narrow terminals the logo is smallened or hidden.
- Alignment uses visible width (ANSI codes stripped), so colors never break columns.
- `render_diff()` shows only fields where `resolved != real`.
- `render_sources()` annotates each field with `[real]`/`[default]`/`[profile]`/`[cli]`.

## Configuration

- Loaded via `tomllib` (no eval/exec). Sections: `[default]`, `[profiles.NAME]`,
  `[appearance]`, `[display]`.
- `validate_config()` checks TOML syntax, unknown sections/keys, and value types.
- Standalone profile files (`--profile-file`, `--export-profile`) are data-only:
  scalar key/value pairs, flat or under a `[profile]` table. Nested tables other
  than `[profile]` are ignored. Loading never executes code.

## Cross-platform detection

`collectors/common.py: collect_all(...)` returns a `SystemInfo` of real values.
Common fields (username, hostname, arch, uptime, memory, disk, battery) are
platform-independent via `psutil`; OS-specific fields (os-release, kernel, shell,
DE, GPU) branch per platform. Every probe is wrapped so failures degrade to an
empty/unavailable value rather than raising.

## Security model

- No `eval`/`exec`; TOML is parsed, never executed.
- No network calls anywhere (no IP detection, no telemetry, no update checks).
- Profiles are data-only; sharing a profile file cannot run code.
- No secrets collection.

## Testing structure

`tests/` has one file per `src/larpfetch` module. Key invariants covered:

- `--real-shit` ignores default profile, selected profile, `--profile-file`, and CLI overrides (`test_integration.py`, `test_resolver.py`).
- Config loading, display layout, profile resolution, logo selection, ANSI
  alignment, `NO_COLOR`, collector degradation, easter-egg determinism, and the
  installable entry point.
- Platform-specific calls are mocked in unit tests.

Run with `just check` (ruff + pytest).
