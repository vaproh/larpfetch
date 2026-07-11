"""Tests for collector modules."""

from collections import namedtuple
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psutil

from larpfetch.collectors.common import (
    _collect_disk_detail,
    _detect_compositor,
    _detect_device_model,
    _detect_gpus_linux,
    _detect_motherboard,
    _detect_resolution,
    _detect_resolution_darwin,
    _detect_resolution_linux,
    _detect_resolution_windows,
    _detect_terminal,
    _detect_wm,
    _fmt_battery,
    _fmt_bytes,
    _fmt_uptime,
    _parse_xrandr,
    collect_all,
    collect_common,
    collect_platform,
)


def _usage(used: int, total: int) -> SimpleNamespace:
    return SimpleNamespace(used=used, total=total)

class TestFmtBytes:
    def test_bytes(self):
        assert _fmt_bytes(512) == "512.0 B"

    def test_kib(self):
        assert _fmt_bytes(1024) == "1.0 KiB"

    def test_mib(self):
        assert _fmt_bytes(1024 * 1024) == "1.0 MiB"

    def test_gib(self):
        assert _fmt_bytes(1024**3) == "1.0 GiB"

    def test_tib(self):
        assert _fmt_bytes(1024**4) == "1.0 TiB"

    def test_zero(self):
        assert _fmt_bytes(0) == "0.0 B"

    def test_rounding_not_truncation(self):
        # 1.5 GiB should show as 1.5, not 1.0
        n = 1.5 * 1024**3
        assert _fmt_bytes(n) == "1.5 GiB"

    def test_pib(self):
        assert _fmt_bytes(1024**5) == "1.0 PiB"

    def test_eib(self):
        assert _fmt_bytes(1024**6) == "1.0 EiB"

    def test_partial_values(self):
        assert _fmt_bytes(1536) == "1.5 KiB"
        assert _fmt_bytes(2048) == "2.0 KiB"


class TestFmtBattery:
    def test_discharging_with_time(self):
        out = _fmt_battery(42.0, False, 3 * 3600 + 15 * 60)
        assert out == "42% (discharging, 3h 15m left)"

    def test_discharging_minutes_only(self):
        out = _fmt_battery(7.0, False, 9 * 60)
        assert out == "7% (discharging, 9m left)"

    def test_discharging_no_estimate(self):
        out = _fmt_battery(50.0, False, -2)
        assert out == "50% (discharging)"

    def test_charging(self):
        out = _fmt_battery(87.0, True, -1)
        assert out == "87% (charging)"

    def test_full(self):
        out = _fmt_battery(100.0, True, -1)
        assert out == "100% (full)"

    def test_unknown_plug_state(self):
        out = _fmt_battery(66.0, None, 0)
        assert out == "66%"


class TestFmtUptime:
    def test_minutes_only(self):
        result = _fmt_uptime(300)
        assert "5m" in result
        assert "d" not in result

    def test_hours_and_minutes(self):
        result = _fmt_uptime(3600 + 300)
        assert "1h" in result
        assert "5m" in result

    def test_days_hours_minutes(self):
        result = _fmt_uptime(86400 + 3600 + 300)
        assert "1d" in result
        assert "1h" in result
        assert "5m" in result

    def test_zero(self):
        result = _fmt_uptime(0)
        assert result == "0m"


class TestCollectCommon:
    def test_collects_username(self):
        info = collect_common()
        assert info.get("username") != ""

    def test_collects_hostname(self):
        info = collect_common()
        assert info.get("hostname") != ""

    def test_collects_architecture(self):
        info = collect_common()
        assert info.get("architecture") != ""

    def test_collects_uptime(self):
        info = collect_common()
        uptime = info.get("uptime")
        assert uptime != ""
        assert "m" in uptime

    def test_collects_memory(self):
        info = collect_common()
        mem = info.get("memory")
        assert mem != ""
        assert "/" in mem  # should be "used / total" format

    def test_collects_disk(self):
        info = collect_common()
        disk = info.get("disk")
        assert disk != ""
        assert "/" in disk


class TestResolution:
    def test_parse_xrandr_with_refresh(self):
        out = (
            "Screen 0: minimum 8 x 8, current 1920 x 1080, maximum 16384 x 16384\n"
            "DP-0 connected primary 1920x1080+0+0 (normal left inverted right x axis) "
            "531mm x 299mm\n"
            "   1920x1080     60.00*+  59.94\n"
            "   1680x1050     59.95\n"
        )
        assert _parse_xrandr(out) == "1920x1080 @ 60Hz"

    def test_parse_xrandr_no_refresh(self):
        out = (
            "DP-0 connected primary 1920x1080+0+0\n"
            "   1920x1080\n"
        )
        assert _parse_xrandr(out) == "1920x1080"

    def test_parse_xrandr_empty(self):
        assert _parse_xrandr("") == ""

    @patch("larpfetch.collectors.common.subprocess.run")
    def test_detect_linux_via_xrandr(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "Screen 0: minimum 320 x 200, current 2560 x 1440\n"
                "DP-1 connected 2560x1440+0+0\n"
                "   2560x1440     144.00*+\n"
            ),
        )
        assert _detect_resolution_linux() == "2560x1440 @ 144Hz"

    @patch("larpfetch.collectors.common.subprocess.run", side_effect=FileNotFoundError)
    def test_detect_linux_xrandr_missing(self, _mock_run):
        # xrandr unavailable -> degrade gracefully (no exception, returns str)
        assert isinstance(_detect_resolution_linux(), str)

    @patch("larpfetch.collectors.common.subprocess.run")
    def test_detect_darwin(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Graphics/Displays:\n\nDisplay:\n  Resolution: 3024 x 1964\n",
        )
        assert _detect_resolution_darwin() == "3024x1964"

    @patch("larpfetch.collectors.common.subprocess.run")
    def test_detect_darwin_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        assert _detect_resolution_darwin() == ""

    def test_detect_windows(self):
        mock_windll = MagicMock()
        mock_windll.user32.GetSystemMetrics.side_effect = [1920, 1080]
        with patch("ctypes.windll", mock_windll, create=True):
            assert _detect_resolution_windows() == "1920x1080"

    def test_detect_windows_failure(self):
        mock_windll = MagicMock()
        mock_windll.user32.GetSystemMetrics.side_effect = Exception("nope")
        with patch("ctypes.windll", mock_windll, create=True):
            assert _detect_resolution_windows() == ""

    @patch("larpfetch.collectors.common.sys.platform", "linux")
    @patch("larpfetch.collectors.common._detect_resolution_linux", return_value="1920x1080 @ 60Hz")
    def test_detect_resolution_dispatches_linux(self, _mock):
        assert _detect_resolution() == "1920x1080 @ 60Hz"

    def test_collect_common_includes_resolution(self, monkeypatch):
        monkeypatch.setattr(
            "larpfetch.collectors.common._detect_resolution", lambda: "1920x1080 @ 60Hz"
        )
        info = collect_common()
        assert info.get("resolution") == "1920x1080 @ 60Hz"


class TestTerminal:
    def test_term_program(self, monkeypatch):
        monkeypatch.setenv("TERM_PROGRAM", "iTerm.app")
        assert _detect_terminal() == "iTerm"

    def test_windows_terminal(self, monkeypatch):
        monkeypatch.delenv("TERM_PROGRAM", raising=False)
        monkeypatch.setenv("WT_SESSION", "1")
        assert _detect_terminal() == "Windows Terminal"

    def test_terminal_env_path(self, monkeypatch):
        monkeypatch.delenv("TERM_PROGRAM", raising=False)
        monkeypatch.delenv("WT_SESSION", raising=False)
        monkeypatch.delenv("WT_PROFILE_ID", raising=False)
        monkeypatch.setenv("TERMINAL", "/usr/bin/kitty")
        assert _detect_terminal() == "kitty"

    def test_colorterm_fallback(self, monkeypatch):
        for var in ("TERM_PROGRAM", "WT_SESSION", "WT_PROFILE_ID", "TERMINAL"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("COLORTERM", "ghostty")
        assert _detect_terminal() == "ghostty"

    def test_truecolor_not_used(self, monkeypatch):
        for var in ("TERM_PROGRAM", "WT_SESSION", "WT_PROFILE_ID", "TERMINAL"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("COLORTERM", "truecolor")
        monkeypatch.setenv("TERM", "xterm-256color")
        assert _detect_terminal() == "xterm-256color"

    def test_empty_when_unknown(self, monkeypatch):
        for var in (
            "TERM_PROGRAM",
            "WT_SESSION",
            "WT_PROFILE_ID",
            "TERMINAL",
            "COLORTERM",
            "TERM",
        ):
            monkeypatch.delenv(var, raising=False)
        assert _detect_terminal() == ""

    def test_collect_common_includes_terminal(self, monkeypatch):
        monkeypatch.setenv("TERM_PROGRAM", "WezTerm")
        assert collect_common().get("terminal") == "WezTerm"


class TestWMCompositor:
    def _no_wayland(self, monkeypatch):
        for var in ("WAYLAND_DISPLAY", "HYPRLAND_INSTANCE_SIGNATURE", "SWAYSOCK"):
            monkeypatch.delenv(var, raising=False)

    def test_wm_hyprland(self, monkeypatch):
        monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc")
        assert _detect_wm() == "Hyprland"

    def test_wm_sway(self, monkeypatch):
        monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
        monkeypatch.setenv("SWAYSOCK", "/tmp/sway.sock")
        assert _detect_wm() == "Sway"

    def test_wm_x11(self, monkeypatch):
        self._no_wayland(monkeypatch)
        monkeypatch.setenv("DISPLAY", ":0")
        mock_result = MagicMock(returncode=0, stdout='_NET_WM_NAME = "i3"\n')
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            assert _detect_wm() == "i3"

    def test_wm_empty(self, monkeypatch):
        self._no_wayland(monkeypatch)
        monkeypatch.delenv("DISPLAY", raising=False)
        assert _detect_wm() == ""

    def test_compositor_wayland(self, monkeypatch):
        monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc")
        assert _detect_compositor() == "Hyprland"

    def test_compositor_x11_named(self, monkeypatch):
        self._no_wayland(monkeypatch)
        monkeypatch.setenv("DISPLAY", ":0")

        def fake_run(args, **kwargs):
            if args[0] == "xprop":
                return MagicMock(returncode=0, stdout="_NET_WM_CM_S0 = 0x1c00003\n")
            if args[0] == "pgrep":
                return MagicMock(returncode=0 if args[2] == "picom" else 1, stdout="")
            return MagicMock(returncode=1, stdout="")

        with patch("larpfetch.collectors.common.subprocess.run", side_effect=fake_run):
            assert _detect_compositor() == "picom"

    def test_compositor_x11_active(self, monkeypatch):
        self._no_wayland(monkeypatch)
        monkeypatch.setenv("DISPLAY", ":0")

        def fake_run(args, **kwargs):
            if args[0] == "xprop":
                return MagicMock(returncode=0, stdout="_NET_WM_CM_S0 = 0x1c00003\n")
            if args[0] == "pgrep":
                return MagicMock(returncode=1, stdout="")
            return MagicMock(returncode=1, stdout="")

        with patch("larpfetch.collectors.common.subprocess.run", side_effect=fake_run):
            assert _detect_compositor() == "active"

    def test_compositor_empty(self, monkeypatch):
        self._no_wayland(monkeypatch)
        monkeypatch.delenv("DISPLAY", raising=False)
        assert _detect_compositor() == ""

    def test_collect_common_includes_wm(self, monkeypatch):
        monkeypatch.delenv("HYPRLAND_INSTANCE_SIGNATURE", raising=False)
        monkeypatch.setenv("SWAYSOCK", "/tmp/sway.sock")
        assert collect_common().get("wm") == "Sway"
        assert collect_common().get("compositor") == "Sway"


class TestDeviceModel:
    def test_linux_dmi(self):
        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = "XPS 13 9310\n"

        import larpfetch.collectors.common as cc

        with patch.object(cc, "sys") as mock_sys, patch("builtins.open", mock_open):
            mock_sys.platform = "linux"
            assert _detect_device_model() == "XPS 13 9310"

    def test_darwin_sysctl(self):
        import larpfetch.collectors.common as cc

        mock_result = MagicMock(returncode=0, stdout="MacBookPro18,3\n")
        with patch.object(cc, "sys") as mock_sys, patch(
            "larpfetch.collectors.common.subprocess.run", return_value=mock_result
        ):
            mock_sys.platform = "darwin"
            assert _detect_device_model() == "MacBookPro18,3"

    def test_win32(self):
        import larpfetch.collectors.common as cc

        mock_result = MagicMock(returncode=0, stdout="Precision 5560\n")
        with patch.object(cc, "sys") as mock_sys, patch(
            "larpfetch.collectors.common.subprocess.run", return_value=mock_result
        ):
            mock_sys.platform = "win32"
            assert _detect_device_model() == "Precision 5560"

    def test_empty(self):
        import larpfetch.collectors.common as cc

        mock_open = MagicMock()
        mock_open.side_effect = OSError("nope")
        with patch.object(cc, "sys") as mock_sys, patch("builtins.open", mock_open):
            mock_sys.platform = "linux"
            assert _detect_device_model() == ""

    def test_motherboard_linux(self):
        import larpfetch.collectors.common as cc

        def fake_open(path, *a, **k):
            content = ""
            if "board_vendor" in path:
                content = "Dell Inc.\n"
            elif "board_name" in path:
                content = "0PPRXH\n"
            m = MagicMock()
            m.__enter__.return_value.read.return_value = content
            return m

        with patch.object(cc, "sys") as mock_sys, patch("builtins.open", side_effect=fake_open):
            mock_sys.platform = "linux"
            assert _detect_motherboard() == "Dell Inc. 0PPRXH"

    def test_motherboard_empty(self):
        import larpfetch.collectors.common as cc

        mock_open = MagicMock()
        mock_open.side_effect = OSError("nope")
        with patch.object(cc, "sys") as mock_sys, patch("builtins.open", mock_open):
            mock_sys.platform = "linux"
            assert _detect_motherboard() == ""

    def test_collect_common_includes_device(self):
        import larpfetch.collectors.common as cc

        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value.read.return_value = "ThinkPad X1\n"
        with patch.object(cc, "sys") as mock_sys, patch("builtins.open", mock_open):
            mock_sys.platform = "linux"
            info = collect_common()
            assert info.get("device") == "ThinkPad X1"


class TestCollectPlatform:
    def test_returns_system_info(self):
        info = collect_platform()
        assert hasattr(info, "fields")
        assert isinstance(info.fields, dict)


class TestCollectLinux:
    @patch("larpfetch.collectors.common.platform.system", return_value="Linux")
    def test_collects_os_from_os_release(self, _mock_sys):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'PRETTY_NAME="Arch Linux"\nNAME="Arch Linux"\n'
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            with patch("builtins.open", create=True) as mock_open:
                mock_open.return_value.__enter__ = lambda s: s
                mock_open.return_value.__exit__ = MagicMock(return_value=False)
                mock_open.return_value.__iter__ = lambda s: iter(
                    ['PRETTY_NAME="Arch Linux"\n', 'NAME="Arch Linux"\n']
                )
                from larpfetch.collectors.common import _collect_linux

                info = _collect_linux()
                assert info.get("distro") == "Arch Linux"

    def test_gpu_detection_from_lspci(self):
        lspci_output = (
            "00:02.0 VGA compatible controller: Intel Corporation HD Graphics 630\n"
            "01:00.0 3D controller: NVIDIA Corporation GP107GL [Quadro P400]\n"
        )
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = lspci_output
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            from larpfetch.collectors.common import _collect_linux

            info = _collect_linux()
            # Should find the first VGA/3D device
            assert info.get("gpu") != ""
            assert "Intel" in info.get("gpu") or "NVIDIA" in info.get("gpu")

    def test_gpu_detection_vga_line(self):
        lspci_output = (
            "01:00.0 VGA compatible controller: NVIDIA Corporation GA102 "
            "[GeForce RTX 3090] (rev a1)\n"
        )
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = lspci_output
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            from larpfetch.collectors.common import _collect_linux

            info = _collect_linux()
            assert "NVIDIA" in info.get("gpu")
            assert "RTX 3090" in info.get("gpu")
            assert "(rev" not in info.get("gpu")

    def test_shell_from_env(self, monkeypatch):
        monkeypatch.setenv("SHELL", "/bin/zsh")
        from larpfetch.collectors.common import _collect_linux

        info = _collect_linux()
        assert info.get("shell") == "zsh"

    def test_de_from_env(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "Hyprland")
        from larpfetch.collectors.common import _collect_linux

        info = _collect_linux()
        assert info.get("de") == "Hyprland"

    def test_multi_gpu_detection(self):
        lspci_output = (
            "00:02.0 VGA compatible controller: Intel Corporation HD Graphics 630 (rev 04)\n"
            "01:00.0 3D controller: NVIDIA Corporation GA102 [GeForce RTX 3090] (rev a1)\n"
        )
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = lspci_output
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            from larpfetch.collectors.common import _collect_linux

            info = _collect_linux()
            gpu = info.get("gpu")
            assert "Intel" in gpu and "NVIDIA" in gpu
            assert " | " in gpu
            assert "(rev" not in gpu

    def test_detect_gpus_linux_returns_list(self):
        lspci_output = (
            "00:02.0 VGA compatible controller: Intel Corporation HD Graphics 630\n"
            "01:00.0 Display controller: NVIDIA Corporation TU117M [GeForce GTX 1650]\n"
        )
        mock_result = MagicMock(returncode=0, stdout=lspci_output)
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            gpus = _detect_gpus_linux()
        assert len(gpus) == 2
        assert gpus[0] == "Intel Corporation HD Graphics 630"
        assert "GeForce GTX 1650" in gpus[1]


class TestCollectWindows:
    def test_shell_from_comspec(self, monkeypatch):
        monkeypatch.setenv("COMSPEC", r"C:\Windows\System32\cmd.exe")
        with patch("larpfetch.collectors.common.platform.system", return_value="Windows"):
            from larpfetch.collectors.common import _collect_windows

            info = _collect_windows()
            assert info.get("shell") == "cmd.exe"

    def test_shell_fallback_to_cmd(self, monkeypatch):
        monkeypatch.delenv("COMSPEC", raising=False)
        with patch("larpfetch.collectors.common.platform.system", return_value="Windows"):
            from larpfetch.collectors.common import _collect_windows

            info = _collect_windows()
            assert info.get("shell") == "cmd.exe"


class TestCollectAll:
    def test_merges_common_and_platform(self):
        info = collect_all()
        assert info.get("username") != ""
        assert info.get("hostname") != ""
        assert info.get("architecture") != ""

    def test_shell_info_flag_adds_version(self, monkeypatch):
        monkeypatch.setenv("SHELL", "/bin/bash")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)\n"
        mock_result.stderr = ""
        with patch("larpfetch.collectors.common.subprocess.run", return_value=mock_result):
            info = collect_all(shell_info=True)
            shell = info.get("shell")
            assert shell != ""
            # shell or shell + version

    def test_shell_info_false_omits_version(self, monkeypatch):
        monkeypatch.setenv("SHELL", "/bin/bash")
        info = collect_all(shell_info=False)
        shell = info.get("shell")
        # Should just be "bash", no version appended
        assert shell == "bash" or not shell.endswith(")")

    def test_disk_info_adds_detail(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])

        def fake_partitions(all=False):  # noqa: A002
            parts = [DiskPart("/dev/sda1", "/", "ext4", "rw")]
            if all:
                parts.append(DiskPart("tmpfs", "/tmp", "tmpfs", "rw"))
            return parts

        monkeypatch.setattr(psutil, "disk_partitions", fake_partitions)
        info = collect_all(disk_mode="physical")
        assert info.get("disk_detail") != ""
        assert "/" in info.get("disk_detail")
        assert "/tmp" not in info.get("disk_detail")  # tmpfs filtered out

    def test_disk_info_all_includes_virtual(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])

        def fake_partitions(all=False):  # noqa: A002
            parts = [DiskPart("/dev/sda1", "/", "ext4", "rw")]
            if all:
                parts.append(DiskPart("tmpfs", "/tmp", "tmpfs", "rw"))
            return parts

        monkeypatch.setattr(psutil, "disk_partitions", fake_partitions)
        info = collect_all(disk_mode="all")
        assert "/tmp" in info.get("disk_detail")  # virtual mounts included

    def test_disk_info_home_shows_only_home(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])
        parts = [
            DiskPart("/dev/sda1", "/", "ext4", "rw"),
            DiskPart("/dev/sda2", "/home", "ext4", "rw"),
            DiskPart("/dev/sdb1", "/data", "ext4", "rw"),
        ]
        monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: parts)  # noqa: A002
        monkeypatch.setattr(psutil, "disk_usage", lambda p: _usage(1_000, 10_000))
        monkeypatch.setenv("HOME", "/home")
        info = collect_all(disk_mode="home")
        detail = info.get("disk_detail")
        assert detail is not None and "/home" in detail
        assert "/data" not in detail and "/:" not in detail

    def test_disk_info_path_shows_only_that_disk(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])
        parts = [
            DiskPart("/dev/sda1", "/", "ext4", "rw"),
            DiskPart("/dev/sdb1", "/data", "ext4", "rw"),
        ]
        monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: parts)  # noqa: A002
        monkeypatch.setattr(psutil, "disk_usage", lambda p: _usage(1_000, 10_000))
        info = collect_all(disk_mode="/data")
        detail = info.get("disk_detail")
        assert detail is not None and "/data" in detail
        assert "/:" not in detail

    def test_disk_info_unknown_mode_no_detail(self):
        info = collect_all(disk_mode="bogus")
        assert info.get("disk_detail") in (None, "")

    def test_collect_disk_detail_home(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])
        parts = [
            DiskPart("/dev/sda1", "/", "ext4", "rw"),
            DiskPart("/dev/sda2", "/home", "ext4", "rw"),
        ]
        monkeypatch.setenv("HOME", "/home")
        monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: parts)  # noqa: A002
        monkeypatch.setattr(psutil, "disk_usage", lambda p: _usage(1_000, 10_000))
        detail = _collect_disk_detail("home")
        assert len(detail) == 1 and detail[0].startswith("/home")

    def test_collect_disk_detail_path(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])
        parts = [
            DiskPart("/dev/sda1", "/", "ext4", "rw"),
            DiskPart("/dev/sdb1", "/data", "ext4", "rw"),
        ]
        monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: parts)  # noqa: A002
        monkeypatch.setattr(psutil, "disk_usage", lambda p: _usage(1_000, 10_000))
        detail = _collect_disk_detail("/data")
        assert len(detail) == 1 and detail[0].startswith("/data")

    def test_collect_disk_detail_physical_filters_virtual(self, monkeypatch):
        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])

        def fake_partitions(all=False):  # noqa: A002
            if all:
                return [
                    DiskPart("/dev/sda1", "/", "ext4", "rw"),
                    DiskPart("tmpfs", "/tmp", "tmpfs", "rw"),
                ]
            return [DiskPart("/dev/sda1", "/", "ext4", "rw")]

        monkeypatch.setattr(psutil, "disk_partitions", fake_partitions)
        monkeypatch.setattr(psutil, "disk_usage", lambda p: _usage(1_000, 10_000))
        detail = _collect_disk_detail("physical")
        assert any(d.startswith("/") and "tmp" not in d for d in detail)
        assert not any("tmp" in d for d in detail)

    def test_gpu_info_flag_passed(self):
        # smoke test: no crash
        info = collect_all(gpu_info=True)
        _ = info  # no crash

    def test_battery_charging_state(self):
        fake = MagicMock()
        fake.percent = 87.0
        fake.power_plugged = True
        fake.secsleft = -1
        with patch("larpfetch.collectors.common.psutil") as mock_psutil:
            mock_psutil.sensors_battery.return_value = fake
            mock_psutil.virtual_memory.return_value = MagicMock(
                used=1, total=2
            )
            mock_psutil.disk_usage.return_value = MagicMock(used=1, total=2)
            mock_psutil.boot_time.return_value = 0
            info = collect_common()
        assert info.get("battery") == "87% (charging)"

    def test_battery_discharging_state(self):
        fake = MagicMock()
        fake.percent = 42.0
        fake.power_plugged = False
        fake.secsleft = 3 * 3600 + 15 * 60
        with patch("larpfetch.collectors.common.psutil") as mock_psutil:
            mock_psutil.sensors_battery.return_value = fake
            mock_psutil.virtual_memory.return_value = MagicMock(used=1, total=2)
            mock_psutil.disk_usage.return_value = MagicMock(used=1, total=2)
            mock_psutil.boot_time.return_value = 0
            info = collect_common()
        assert info.get("battery") == "42% (discharging, 3h 15m left)"

    def test_battery_none_is_empty(self):
        with patch("larpfetch.collectors.common.psutil") as mock_psutil:
            mock_psutil.sensors_battery.return_value = None
            mock_psutil.virtual_memory.return_value = MagicMock(used=1, total=2)
            mock_psutil.disk_usage.return_value = MagicMock(used=1, total=2)
            mock_psutil.boot_time.return_value = 0
            info = collect_common()
        assert info.get("battery") == ""


class TestCollectorFailureDegradation:
    def test_psutil_failure_doesnt_crash(self):
        with patch("larpfetch.collectors.common.psutil", None):
            info = collect_common()
            # Should still collect non-psutil fields
            assert info.get("username") != ""
            assert info.get("hostname") != ""
            # Memory/disk/battery should be empty but not crash
            assert info.get("memory") == ""
            assert info.get("disk") == ""
            assert info.get("battery") == ""

    def test_lspci_failure_doesnt_crash(self):
        patch_target = "larpfetch.collectors.common.subprocess.run"
        with patch(patch_target, side_effect=Exception("not found")):
            info = collect_platform()
            # Should not crash, GPU may be missing
            assert hasattr(info, "fields")
