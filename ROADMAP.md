# Roadmap

> **Autonomous cadence:** This roadmap is 100% implemented by autonomous coding agents — no human writes code here. A theme (e.g. `v1.5`) is implemented incrementally into CHANGELOG's `## Unreleased` section and shipped as a single minor version `vX.Y.0` once its items are complete (or a deliberate, documented subset). See [AGENTS.md](AGENTS.md) for the full versioning and release policy.

## v1.1.0 — Shipped

- `--logo NAME` flag to pick any logo directly
- `--list-logos` to show all available logo names
- `--list-logos --search <query>` to filter logos
- Pipe mode: suppress logo when stdout is not a TTY
- `--cols N` to force column width
- `--distro NAME` quick distro LARP
- `--small` use small ASCII art variant

## v1.2.0 — Shipped

- JSON output (`--json`)
- Package count detection (apt, pacman, brew, winget)
- `--shell-info` for shell version detection
- `--gpu-info` for detailed GPU detection
- `--disk-info` for per-disk breakdown

## v1.3 — Daily-Driver Customization — Shipped

Let users control exactly what their fetch looks like.

- **Declarative display layout** — control which fields appear, their order, custom labels, separators, spacing, and whether unavailable fields are hidden ✅
- **Display density presets** — `--minimal`, `--compact`, `--full` backed by the declarative layout system ✅
- **Terminal width responsiveness** — renderer adapts to narrow terminals (split panes, mobile SSH, small windows) ✅
- **`--generate-config`** — produce a starter config with commented examples ✅
- **Better README visuals** — side-by-side reality vs delusion comparison, explicit "Not just a meme" section ✅
- **Profile-specific logos** — profiles can set a `logo` (built-in name or inline art); user can still override via `--logo` ✅
- **Self-documenting config example** — `--generate-config` emits a fully commented, self-explanatory template ✅

> Themes (separate from profiles) are deferred to v1.6.

## v1.4 — Reality vs Delusion — Shipped

Strengthen what makes larpfetch unique.

- **`--diff-real`** — show only fields where the displayed identity differs from real detection ✅
- **`--show-sources`** — inspect where every value came from (detected, config, profile, CLI) ✅
- **JSON provenance** — `--json --with-sources` exposes value, source, and real_value per field ✅
- **`--export-profile`** — detect real system and export as a reusable TOML profile ✅
- **Standalone shareable profile files** — `--profile-file nasa.toml` to load profiles outside main config ✅
- **Profile inspection** — `--inspect-profile nasa` shows source, fields, and logo ✅
- **Profile security model** — shareable profiles are data-only; no arbitrary command execution ✅
- **Config validation** — `--check-config` validates TOML syntax, unknown fields, and value types ✅

## v1.5 — Daily-Driver System Information

Cover the most useful missing real-system fields.

- Battery percentage and charging/discharging state ✅
- Display resolution and refresh rate ✅
- Desktop environment / window manager / compositor ✅
- Terminal emulator detection ✅
- Device model and motherboard model
- Better multi-GPU handling (integrated + dedicated + eGPU)
- Better multi-disk handling (per-disk breakdown, filter virtual mounts)
- `--disk-info all` / `--disk-info physical`

## v1.6 — Themes and Visual Polish

Give users deep visual customization.

- **Proper theme system** — separate from profiles (a profile answers "what computer", a theme answers "how it looks")
- Built-in themes: catppuccin, dracula, nord, gruvbox, solarized, tokyo-night
- Custom key/value colors, separators, bold/dim formatting, spacing, accent colors
- **Field groups / sections** — optional grouped layouts (SYSTEM, HARDWARE, ENVIRONMENT)
- **Conditional fields** — show/hide based on availability, platform, or flags
- **Custom separators and symbols** — `->`, `:`, `•`, `│`
- **ASCII-only mode** — `--ascii-only` for terminal compatibility
- **Unicode width correctness** — emoji, CJK, combining characters, wide chars
- **Accessibility** — no reliance on color alone, high-contrast themes, configurable symbols

## v1.7 — Diagnostics and Tooling

Make bugs easy to understand and report.

- **`--explain FIELD`** — shows value, source, probe time, fallbacks for individual fields
- **`--diagnose`** — full system diagnostics (OK/WARN/ERROR per detector)
- **`--timings`** — per-field detection timing breakdown
- **`--check-config`** — validate config file
- **Shell completions** — bash, zsh, fish, powershell (flags, profiles, themes, fields)
- **Man page** — `man larpfetch`
- **Error visibility without ugly output** — clean daily output, detailed debug mode
- **Performance / probe timing** — optional `--timings` flag for per-field detection cost
- **Timeouts for external probes** — every subprocess detector has a reasonable timeout
- **Copy-friendly output** — `--markdown`, `--plain`, `--no-logo`

## v1.8 — Deeper Platform Support

- **Privacy mode** — `--privacy` redacts user, hostname, local IP
- **Screenshot / share mode** — `--share` hides sensitive info, balanced layout
- **Multi-GPU display** — GPU 1, GPU 2 with type labels
- **Multi-disk display** — clear per-disk info, skip virtual mounts
- **Better package detection details** — per-manager counts (pacman + flatpak + pipx...)
- **Custom computed fields** — safe environment variable references (`editor = "$EDITOR"`), opt-in only

## v2.0 — Stability

Establish stable interfaces.

- **Stable JSON schema** — documented, versioned (`schema_version` field)
- **Stable config schema** — `[display]`, `[theme]`, `[privacy]` sections
- **Versioned profile format** — `profile_version = 1` for standalone files
- **Config migration support** — `--migrate-config` for schema bumps
- **Strong cross-platform CI** — Linux, Windows, macOS across supported Python versions
- **Documented compatibility guarantees**
- **Performance targets** — basic fetch under 100ms, expensive probes optional/cached
- **Refined detection architecture**

## v2.1+ — Possible (if demand warrants)

- **Profile inheritance** — one profile extends another (`extends = "nasa"`)
- **`--compare`** — diff two profiles or compare real vs profile
- **`--random-profile`** — pick a random profile each run
- **`--hallucinate`** — generate absurd but structured fake system info (deterministic, no AI)
- **`--explain-authenticity`** — breakdown of the authenticity score
- **Community profile packs** — shareable TOML collections via git, no central registry
- **`--demo`** — auto-cycle through real system, a profile, overrides, and `--real-shit`
- **Cache expensive detection results** — OS, CPU, GPU model (only if profiling proves need)

## Product vision

> "I installed this because it was funny. I kept it because it's actually a good fetch tool."

larpfetch should not try to beat Fastfetch by having more fields. It wins by having a clearer personality, a better identity/override model, easier customization, strong scripting support, and features that no normal fetch tool would naturally have.

### Design principles

Every new feature should either:

1. Make larpfetch better as a real daily-driver fetch tool.
2. Strengthen its unique real-vs-fake identity system.
3. Improve customization, scripting, debugging, or sharing.

If a feature does none of these, it probably does not belong.

### What not to build

- GUI — keep it a terminal tool
- Built-in weather, benchmarks, network speed tests, process management — different product categories
- AI-generated profiles — unnecessary latency, complexity, and privacy concerns
- Massive plugin architecture too early — shareable TOML files are enough
- A central community registry before actual demand exists
- Arbitrary command execution from downloaded profiles — serious security risk
- Public IP detection by default — unnecessary network call and privacy issue
- Matching every single Fastfetch field — larpfetch should have its own identity
- Hundreds of styling CLI flags — complex styling belongs in configuration

### The five most important features

1. **Declarative display customization** — users control what appears, in what order, under what labels
2. **`--diff-real`** — directly expresses the project's central idea
3. **`--show-sources`** — makes the precedence system visible and debuggable
4. **More daily-driver fields** — battery, resolution, DE/WM, terminal, device model
5. **Proper themes** — separate identity from presentation

### The most uniquely larpfetch feature

```
$ larpfetch -p nasa --diff-real

OS      Arch Linux          -> NASA Mission Control
CPU     Ryzen 7 7840HS      -> Quantum Potato 9000
RAM     32 GB               -> 69 PiB
GPU     Radeon 780M         -> RTX 6090 Ti Super Ultra
```

This directly expresses the project's central idea: reality exists, but the user's delusion is authoritative anyway.
