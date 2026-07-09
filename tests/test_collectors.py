"""Tests for collector modules."""

from unittest.mock import patch

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
        assert _fmt_bytes(1024 ** 3) == "1.0 GiB"

    def test_tib(self):
        assert _fmt_bytes(1024 ** 4) == "1.0 TiB"

    def test_zero(self):
        assert _fmt_bytes(0) == "0.0 B"


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


class TestCollectAll:
    def test_merges_common_and_platform(self):
        info = collect_all()
        assert info.get("username") != ""
        assert info.get("hostname") != ""
        assert info.get("architecture") != ""


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
        with patch("subprocess.run", side_effect=Exception("not found")):
            info = collect_platform()
            # Should not crash, GPU may be missing
            assert hasattr(info, "fields")
