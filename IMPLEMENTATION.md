# larpfetch Implementation Blueprint

## 1. Technical stack

- Python 3.11+
- `psutil`
- `tomllib`
- `argparse`
- `pathlib`
- `platform`
- `getpass`
- `socket`
- `subprocess`
- `shutil`
- `time`
- `os`

Development:

- `pytest`
- `pytest-cov`
- `ruff`

## 2. Build order

### Phase 1: Package skeleton

Create:

```text
pyproject.toml
README.md
LICENSE
src/larpfetch/__init__.py
src/larpfetch/__main__.py
src/larpfetch/cli.py
tests/
```

Expose:

```toml
[project.scripts]
larpfetch = "larpfetch.cli:main"
```

Confirm:

```bash
python -m larpfetch --help
larpfetch --help
```

### Phase 2: Models and real detection

Create a normalized data structure that stores known fields plus custom fields.

Suggested approach:

```python
@dataclass
class SystemInfo:
    fields: OrderedDict[str, str]
```

Or a similarly simple typed structure.

Implement a common collector using standard library and `psutil`.

Then implement platform-specific enrichment.

Every optional probe should fail gracefully.

### Phase 3: Configuration

Implement platform-appropriate default config paths.

Load TOML:

```text
[default]
[profiles.<name>]
[appearance]
```

Return a clear config object containing:

- default profile
- named profiles
- appearance settings

Unknown fields are valid.

### Phase 4: Resolver

Implement one pure resolution function.

Inputs:

- real system values
- default profile
- optional selected profile
- CLI overrides
- `real_shit: bool`

Output:

- resolved display identity
- mode metadata: `real` or `larp`

Pseudo-code:

```python
if real_shit:
    return real_values

resolved = real_values.copy()
resolved.update(default_profile)

if selected_profile:
    resolved.update(selected_profile)

resolved.update(cli_overrides)
return resolved
```

Test this aggressively.

### Phase 5: CLI

Implement parsing for:

```text
-p, --profile NAME
--real-shit
--list-profiles
--show-config
--config PATH
--set KEY=VALUE
--version
```

Parsing requirements:

- Repeated `--set`.
- Split on first `=`.
- Reject empty keys.
- Permit arbitrary string values.
- `--real-shit` must dominate fake inputs.

### Phase 6: Logos

Create original built-in ASCII logos.

Map normalized displayed identity names to logos.

Examples:

```text
arch, arch linux -> arch
windows, windows 11, windows 10 -> windows
macos, mac os, darwin -> macos
ubuntu -> ubuntu
debian -> debian
fedora -> fedora
templeos -> templeos
unknown -> generic
```

The displayed identity determines the logo in LARP mode.

### Phase 7: Renderer

Render:

```text
<logo>    username@hostname
<logo>    -----------------
<logo>    OS: ...
<logo>    Kernel: ...
<logo>    CPU: ...
```

Requirements:

- ANSI color.
- ANSI-stripping width calculation.
- Graceful logo/info height mismatch.
- `NO_COLOR`.
- Stable field ordering.
- Custom fields displayed deterministically.

### Phase 8: Humor and easter eggs

Implement after core functionality is stable.

Suggested mode indicator:

- LARP mode: optional `Authenticity: N%`
- Real mode: optional `Authenticity: 100%`

Potential easter eggs:

- Extremely implausible memory string -> `Source: trust me bro`
- Windows + Arch kernel -> no warning; optionally rare hidden joke.
- Real system crossing conservative high-end thresholds -> `Reality has out-LARPed the LARP.`

Do not make output nondeterministic unless randomness is injectable and testable.

### Phase 9: Tests

Recommended test modules:

```text
tests/test_cli.py
tests/test_config.py
tests/test_resolver.py
tests/test_renderer.py
tests/test_logos.py
tests/test_collectors.py
tests/test_easter_eggs.py
```

The resolver should receive the heaviest unit coverage.

### Phase 10: Documentation and release readiness

README sections:

1. Hero/title/tagline.
2. Demo.
3. Installation with `pipx`.
4. Basic usage.
5. `--real-shit`.
6. Profiles.
7. Configuration.
8. CLI overrides.
9. Cross-platform support.
10. Easter eggs, without spoiling all of them.
11. Development.
12. Testing.
13. Limitations.
14. License.

## 3. Suggested `pyproject.toml`

Use modern PEP 621 metadata. Example shape:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "larpfetch"
version = "0.1.0"
description = "LARP as any distro, hardware, or machine you want."
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["psutil>=5.9"]

[project.scripts]
larpfetch = "larpfetch.cli:main"
```

Before publishing, verify current package-name availability and metadata requirements rather than assuming them.

## 4. Real detection strategy

### Common

Use:

- `getpass.getuser()`
- `socket.gethostname()`
- `platform.machine()`
- `psutil.boot_time()`
- `psutil.virtual_memory()`
- `psutil.disk_usage()`
- `psutil.sensors_battery()` where supported

### Linux

Prefer:

- `/etc/os-release`
- `platform.release()`
- environment variables for shell/DE
- safe optional subprocess probes for GPU/package data

### Windows

Prefer:

- `platform` APIs
- standard environment variables
- PowerShell/CIM only as optional best-effort probes with timeout and safe argument passing

### macOS

Prefer:

- `platform.mac_ver()`
- `platform.release()`
- `system_profiler` only as an optional best-effort probe with timeout

## 5. Error strategy

User-facing configuration errors should produce concise messages and nonzero exit codes.

Optional system-probe failures should degrade silently or to `Unknown`, depending on context.

Debug diagnostics may be added later behind a `--debug` flag, but are not required for v1.

## 6. Performance target

Aim for sub-second startup on normal machines when optional external probes are absent or fast.

Slow probes should:

- have short timeouts
- be avoidable
- never block the entire application indefinitely

## 7. Compatibility principle

Profiles are data, not simulations.

Do not infer compatibility.

Do not reject:

```text
Windows + Arch kernel
macOS + RTX 9090
TempleOS + GNOME
Raspberry Pi + 69 PiB RAM
```

Print what the user configured.

## 8. Definition of done

- Full test suite passes.
- Lint passes.
- Local package build succeeds.
- `pipx install .` succeeds.
- CLI examples in README work.
- `--real-shit` is demonstrably immune to all fake inputs.
- Cross-platform collectors fail gracefully when platform-only facilities are unavailable.
- No needless architecture has metastasized into the codebase.
