"""Cross-platform collectors using standard library and psutil."""

from __future__ import annotations

import getpass
import os
import platform
import socket
import subprocess
import time
from collections import OrderedDict

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
                info.set("battery", f"{bat.percent}%")
    except Exception:
        pass

    # CPU model
    try:
        info.set("cpu", _detect_cpu())
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
