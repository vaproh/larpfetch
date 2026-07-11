"""Cross-platform collectors using standard library and psutil."""

from __future__ import annotations

import getpass
import os
import platform
import re
import socket
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore[assignment]

from larpfetch.models import SystemInfo


def _fmt_bytes(n: float) -> str:
    """Format bytes to human-readable string."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EiB"


def _fmt_uptime(seconds: float) -> str:
    """Format seconds to a human-readable uptime string."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


def _fmt_battery(percent: float, power_plugged: bool | None, secsleft: float) -> str:
    """Format battery percent plus charging/discharging state.

    psutil reports secsleft as a positive estimate, POWER_TIME_UNLIMITED
    (-1) when plugged in with no estimate, or POWER_TIME_UNKNOWN (-2).
    """
    base = f"{percent:.0f}%"
    if power_plugged is None:
        return base
    if power_plugged:
        if percent >= 100:
            return f"{base} (full)"
        return f"{base} (charging)"
    # Discharging
    if secsleft and secsleft > 0:
        mins = int(secsleft // 60)
        hours, rem = divmod(mins, 60)
        if hours:
            left = f"{hours}h {rem}m"
        else:
            left = f"{mins}m"
        return f"{base} (discharging, {left} left)"
    return f"{base} (discharging)"


def _detect_resolution() -> str:
    """Best-effort primary display resolution, optionally with refresh rate.

    Returns strings like ``1920x1080`` or ``1920x1080 @ 60Hz``. Empty on
    failure. Detection is per-platform and degrades gracefully.
    """
    if sys.platform == "darwin":
        return _detect_resolution_darwin()
    if sys.platform == "win32":
        return _detect_resolution_windows()
    return _detect_resolution_linux()


def _parse_xrandr(output: str) -> str:
    """Parse ``xrandr`` output for the current primary resolution + refresh."""
    current: tuple[int, int, float | None] | None = None
    for line in output.splitlines():
        line = line.strip()
        if "*" not in line and "+" not in line:
            continue
        mode = re.search(r"(\d+)x(\d+)\s+.*?(\d+(?:\.\d+)?)\*?\+?", line)
        if not mode:
            mode = re.search(r"(\d+)x(\d+)", line)
            if not mode:
                continue
            current = (int(mode.group(1)), int(mode.group(2)), None)
            continue
        refresh = float(mode.group(3)) if mode.group(3) else None
        current = (int(mode.group(1)), int(mode.group(2)), refresh)
        if "*" in line:
            break
    if not current:
        return ""
    w, h, refresh = current
    if refresh:
        return f"{w}x{h} @ {refresh:.0f}Hz"
    return f"{w}x{h}"


def _detect_resolution_linux() -> str:
    """Linux: prefer ``xrandr``; fall back to a sysfs mode."""
    try:
        result = subprocess.run(
            ["xrandr"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            parsed = _parse_xrandr(result.stdout)
            if parsed:
                return parsed
    except Exception:
        pass

    try:
        card_dirs = sorted(Path("/sys/class/drm").glob("card*-*"))
        for card in card_dirs:
            modes = card / "modes"
            if modes.is_file():
                first = modes.read_text().splitlines()
                if first:
                    return first[0].strip()
    except Exception:
        pass

    return ""


def _detect_resolution_darwin() -> str:
    """macOS: parse ``system_profiler`` display resolution."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return ""
        match = re.search(r"Resolution:\s*(\d+)\s*x\s*(\d+)", result.stdout)
        if match:
            return f"{match.group(1)}x{match.group(2)}"
    except Exception:
        pass
    return ""


def _detect_resolution_windows() -> str:
    """Windows: primary resolution via ``GetSystemMetrics``.

    Refresh rate is not reliably available without display-driver calls, so
    it is omitted on Windows (graceful degradation).
    """
    try:
        import ctypes

        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w and h:
            return f"{w}x{h}"
    except Exception:
        pass
    return ""


def _detect_terminal() -> str:
    """Best-effort terminal emulator detection from the process environment.

    Relies on commonly exported variables (``TERM_PROGRAM``, ``WT_SESSION``,
    ``TERMINAL``, ``COLORTERM``, ``TERM``). Returns "" when nothing useful is
    found. The shell's own name is intentionally not used as a fallback.
    """
    prog = os.environ.get("TERM_PROGRAM", "").strip()
    if prog:
        return prog.replace(".app", "")

    if os.environ.get("WT_SESSION") or os.environ.get("WT_PROFILE_ID"):
        return "Windows Terminal"

    term = os.environ.get("TERMINAL", "").strip()
    if term:
        # May be a full path like /usr/bin/kitty
        return Path(term).name

    colorterm = os.environ.get("COLORTERM", "").strip()
    if colorterm and colorterm.lower() not in ("truecolor", "true"):
        return colorterm

    t = os.environ.get("TERM", "").strip()
    if t:
        return t
    return ""


def _detect_wm() -> str:
    """Best-effort window manager detection.

    Wayland compositors self-identify via env vars; on X11 the root window's
    ``_NET_WM_NAME`` is queried. Returns "" when nothing is found.
    """
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "Hyprland"
    if os.environ.get("SWAYSOCK"):
        return "Sway"
    if os.environ.get("DISPLAY"):
        try:
            result = subprocess.run(
                ["xprop", "-root", "_NET_WM_NAME"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                match = re.search(r'=\s*"?([^"\n]+?)"?\s*$', result.stdout)
                if match:
                    return match.group(1).strip()
        except Exception:
            pass
    return ""


def _process_running(name: str) -> bool:
    """Return True if a process named ``name`` is running (best-effort)."""
    try:
        r = subprocess.run(["pgrep", "-x", name], capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def _detect_compositor() -> str:
    """Best-effort compositor detection.

    On Wayland the compositor is the window manager itself, so the WM name is
    reused. On X11 a compositor owns ``_NET_WM_CM_S0``; the owning process is
    named when recognizable, otherwise reported as ``active``.
    """
    wayland = bool(
        os.environ.get("WAYLAND_DISPLAY")
        or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        or os.environ.get("SWAYSOCK")
    )
    if wayland:
        return _detect_wm()

    if os.environ.get("DISPLAY"):
        try:
            result = subprocess.run(
                ["xprop", "-root", "_NET_WM_CM_S0"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                out = result.stdout
                if "0x0" not in out and "not found" not in out:
                    for proc in ("picom", "compton", "xcompmgr"):
                        if _process_running(proc):
                            return proc
                    return "active"
        except Exception:
            pass
    return ""


def _read_sysfs(path: str) -> str:
    """Read a sysfs file, returning stripped content or "" on any failure."""
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def _detect_windows_field(class_name: str, prop: str) -> str:
    """Query a WMI class property via PowerShell (best-effort)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"(Get-CimInstance {class_name}).{prop}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _detect_device_model() -> str:
    """Best-effort device/model name."""
    if sys.platform == "linux":
        name = _read_sysfs("/sys/devices/virtual/dmi/id/product_name")
        if not name:
            name = _read_sysfs("/sys/devices/virtual/dmi/id/product_version")
        return name
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.model"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""
    if sys.platform == "win32":
        return _detect_windows_field("Win32_ComputerSystem", "Model")
    return ""


def _detect_motherboard() -> str:
    """Best-effort motherboard model (vendor + product)."""
    if sys.platform == "linux":
        vendor = _read_sysfs("/sys/devices/virtual/dmi/id/board_vendor")
        name = _read_sysfs("/sys/devices/virtual/dmi/id/board_name")
        if vendor and name:
            return f"{vendor} {name}"
        return name or vendor
    if sys.platform == "win32":
        return _detect_windows_field("Win32_BaseBoard", "Product")
    return ""


def collect_common(disk_info: bool = False) -> SystemInfo:
    """Collect information common across all platforms."""
    info = SystemInfo(fields=OrderedDict())

    # Username
    try:
        info.set("username", getpass.getuser())
    except Exception:
        pass

    # Hostname
    try:
        info.set("hostname", socket.gethostname())
    except Exception:
        pass

    # Architecture
    try:
        info.set("architecture", platform.machine())
    except Exception:
        pass

    # Uptime
    try:
        if psutil is not None:
            boot = psutil.boot_time()
            info.set("uptime", _fmt_uptime(time.time() - boot))
    except Exception:
        pass

    # Memory
    try:
        if psutil is not None:
            vm = psutil.virtual_memory()
            info.set("memory", f"{_fmt_bytes(vm.used)} / {_fmt_bytes(vm.total)}")
    except Exception:
        pass

    # Disk
    try:
        if psutil is not None:
            du = psutil.disk_usage("/")
            info.set("disk", f"{_fmt_bytes(du.used)} / {_fmt_bytes(du.total)}")
    except Exception:
        pass

    # Per-disk breakdown
    if disk_info and psutil is not None:
        try:
            parts = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    parts.append(
                        f"{part.mountpoint}: {_fmt_bytes(usage.used)}/{_fmt_bytes(usage.total)}"
                    )
                except Exception:
                    continue
            if parts:
                info.set("disk_detail", " | ".join(parts))
        except Exception:
            pass

    # Battery
    try:
        if psutil is not None:
            bat = psutil.sensors_battery()
            if bat is not None:
                info.set("battery", _fmt_battery(bat.percent, bat.power_plugged, bat.secsleft))
    except Exception:
        pass

    # CPU model
    try:
        info.set("cpu", _detect_cpu())
    except Exception:
        pass

    # Device model and motherboard
    try:
        device = _detect_device_model()
        if device:
            info.set("device", device)
    except Exception:
        pass
    try:
        motherboard = _detect_motherboard()
        if motherboard:
            info.set("motherboard", motherboard)
    except Exception:
        pass

    # Terminal emulator
    try:
        terminal = _detect_terminal()
        if terminal:
            info.set("terminal", terminal)
    except Exception:
        pass

    # Window manager and compositor
    try:
        wm = _detect_wm()
        if wm:
            info.set("wm", wm)
    except Exception:
        pass
    try:
        compositor = _detect_compositor()
        if compositor:
            info.set("compositor", compositor)
    except Exception:
        pass

    # Display resolution (and refresh where available)
    try:
        resolution = _detect_resolution()
        if resolution:
            info.set("resolution", resolution)
    except Exception:
        pass

    return info


def _detect_cpu() -> str:
    """Best-effort CPU name detection."""
    # Linux: /proc/cpuinfo
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass

    # macOS: sysctl
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Windows: platform.processor()
    proc = platform.processor()
    if proc:
        return proc

    return "Unknown CPU"


def collect_platform(
    shell_info: bool = False,
    gpu_info: bool = False,
) -> SystemInfo:
    """Collect platform-specific information."""
    system = platform.system()
    if system == "Linux":
        return _collect_linux(shell_info=shell_info, gpu_info=gpu_info)
    elif system == "Darwin":
        return _collect_macos(shell_info=shell_info, gpu_info=gpu_info)
    elif system == "Windows":
        return _collect_windows(shell_info=shell_info, gpu_info=gpu_info)
    return SystemInfo(fields=OrderedDict())


def _collect_linux(
    shell_info: bool = False,
    gpu_info: bool = False,
) -> SystemInfo:
    info = SystemInfo(fields=OrderedDict())

    # OS / distro from /etc/os-release
    os_release: dict[str, str] = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    os_release[key] = value.strip('"')
    except OSError:
        pass

    if os_release.get("PRETTY_NAME"):
        info.set("distro", os_release["PRETTY_NAME"])
        info.set("os", os_release["PRETTY_NAME"])
    elif os_release.get("NAME"):
        info.set("distro", os_release["NAME"])
        info.set("os", os_release["NAME"])

    if os_release.get("VERSION"):
        info.set("os_version", os_release["VERSION"])

    # Kernel
    try:
        info.set("kernel", platform.release())
    except Exception:
        pass

    # Shell
    shell = os.environ.get("SHELL", "")
    if shell:
        info.set("shell", os.path.basename(shell))

    # Desktop environment
    de = os.environ.get("XDG_CURRENT_DESKTOP", "") or os.environ.get("DESKTOP_SESSION", "")
    if de:
        info.set("de", de)

    # GPU via lspci (best-effort)
    try:
        result = subprocess.run(
            ["lspci"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                lower = line.lower()
                if "vga" in lower or "3d" in lower or "display" in lower:
                    # Format: "XX:XX.X Class: vendor device"
                    parts = line.split(": ", 1)
                    if len(parts) >= 2:
                        gpu_desc = parts[1]
                        # Trim the trailing (rev xx) if present
                        if " (" in gpu_desc:
                            gpu_desc = gpu_desc[: gpu_desc.rfind(" (")]
                        info.set("gpu", gpu_desc)
                        break
    except Exception:
        pass

    return info


def _collect_macos(
    shell_info: bool = False,
    gpu_info: bool = False,
) -> SystemInfo:
    info = SystemInfo(fields=OrderedDict())

    # macOS version
    try:
        mac_ver = platform.mac_ver()
        if mac_ver and mac_ver[0]:
            info.set("os", f"macOS {mac_ver[0]}")
            info.set("distro", f"macOS {mac_ver[0]}")
            info.set("os_version", mac_ver[0])
    except Exception:
        pass

    # Kernel
    try:
        info.set("kernel", f"Darwin {platform.release()}")
    except Exception:
        pass

    # Shell
    shell = os.environ.get("SHELL", "")
    if shell:
        info.set("shell", os.path.basename(shell))

    # Desktop environment (macOS = Aqua)
    info.set("de", "Aqua")

    # GPU via system_profiler (best-effort)
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "Chipset Model:" in line or "Chip:" in line:
                    gpu = line.split(":", 1)[1].strip()
                    info.set("gpu", gpu)
                    break
    except Exception:
        pass

    return info


def _collect_windows(
    shell_info: bool = False,
    gpu_info: bool = False,
) -> SystemInfo:
    info = SystemInfo(fields=OrderedDict())

    # Windows version
    try:
        ver = platform.version()
        release = platform.release()
        info.set("os", f"Windows {release} {ver}")
        info.set("os_version", f"{release} {ver}")
    except Exception:
        pass

    # Kernel
    try:
        info.set("kernel", platform.platform())
    except Exception:
        pass

    # Shell - detect from COMSPEC, fallback to cmd.exe
    comspec = os.environ.get("COMSPEC", "")
    if comspec:
        # Handle both Windows (\) and Unix (/) path separators
        shell_name = comspec.replace("\\", "/").split("/")[-1]
        info.set("shell", shell_name)
    else:
        info.set("shell", "cmd.exe")

    # Desktop environment
    info.set("de", "Desktop Window Manager")

    # GPU via WMIC (best-effort)
    try:
        result = subprocess.run(
            ["wmic", "path", "win32_videocontroller", "get", "name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = [
                line.strip()
                for line in result.stdout.splitlines()
                if line.strip() and line.strip() != "Name"
            ]
            if lines:
                info.set("gpu", lines[0])
    except Exception:
        pass

    return info


def collect_all(
    shell_info: bool = False,
    gpu_info: bool = False,
    disk_info: bool = False,
) -> SystemInfo:
    """Collect all available system information."""
    info = collect_common(disk_info=disk_info)
    platform_info = collect_platform(shell_info=shell_info, gpu_info=gpu_info)
    info.update_from(platform_info.to_dict())

    # Package count detection
    pkg = _detect_packages()
    if pkg:
        info.set("package_count", pkg)

    # Shell version detail
    if shell_info:
        shell_ver = _detect_shell_version()
        if shell_ver:
            cur = info.get("shell", "")
            if cur:
                info.set("shell", f"{cur} {shell_ver}")

    # GPU detail
    if gpu_info:
        gpu_drv = _detect_gpu_driver()
        if gpu_drv:
            cur = info.get("gpu", "")
            if cur and gpu_drv:
                info.set("gpu", f"{cur} ({gpu_drv})")

    return info


def _detect_packages() -> str:
    """Detect installed package count from the system package manager."""
    managers = [
        (["dpkg-query", "-f", "${binary:Package}\n", "-W"], lambda o: len(o.strip().splitlines())),
        (["pacman", "-Q", "-q"], lambda o: len(o.strip().splitlines())),
        (["rpm", "-qa", "--queryformat", "%{NAME}\n"], lambda o: len(o.strip().splitlines())),
        (["brew", "list", "--formula"], lambda o: len(o.strip().splitlines())),
        (["winget", "list", "--accept-source-agreements"],
         lambda o: len(o.strip().splitlines()) - 2),
    ]
    for cmd, counter in managers:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                count = counter(result.stdout)
                if count > 0:
                    return str(count)
        except Exception:
            continue
    return ""


def _detect_shell_version() -> str:
    """Detect shell version."""
    shell = os.environ.get("SHELL", "")
    if not shell:
        return ""
    try:
        result = subprocess.run([shell, "--version"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            line = result.stdout.splitlines()[0] if result.stdout else ""
            for word in line.split():
                if word[0].isdigit():
                    return word
    except Exception:
        pass
    return ""


def _detect_gpu_driver() -> str:
    """Detect GPU driver version."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            driver = result.stdout.strip()
            if driver:
                return f"Driver: {driver}"
    except Exception:
        pass
    return ""
