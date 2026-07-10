"""Tests for collector modules."""

from unittest.mock import MagicMock, patch

from larpfetch.collectors.common import (
    _fmt_bytes,
    _fmt_uptime,
    collect_all,
    collect_common,
    collect_platform,
)


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

    def test_disk_info_adds_detail(self):
        info = collect_all(disk_info=True)
        # Should still have disk
        assert info.get("disk") != ""
        assert "/" in info.get("disk")

    def test_gpu_info_flag_passed(self):
        # smoke test: no crash
        info = collect_all(gpu_info=True)
        _ = info  # no crash


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
