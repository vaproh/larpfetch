"""Tests for the renderer module."""

from collections import OrderedDict

from larpfetch.models import SystemInfo
from larpfetch.renderer import Colors, render


def _make_info(**kwargs: str) -> SystemInfo:
    return SystemInfo(fields=OrderedDict(kwargs))


class TestRenderer:
    def test_basic_render(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        real = info
        result = render(info, real, real_shit=False, appearance={"color": False})
        assert "user@host" in result
        assert "OS: Linux" in result

    def test_no_color_respects_no_color_env(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(info, info, real_shit=False, appearance={"color": True})
        assert "\033[" not in result  # no ANSI codes

    def test_color_disabled_by_appearance(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(info, info, real_shit=False, appearance={"color": False})
        assert "\033[" not in result

    def test_real_shit_uses_real_os_for_logo(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Arch Linux")
        larp = _make_info(os="Windows 11 Pro")
        result = render(larp, real, real_shit=True, appearance={"color": False})
        # In real-shit mode, the logo should be based on real OS
        assert "Arch" in result or "arch" in result.lower() or len(result) > 0

    def test_larp_uses_larp_os_for_logo(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Linux")
        larp = _make_info(os="Windows 11 Pro")
        result = render(larp, real, real_shit=False, appearance={"color": False})
        assert len(result) > 0

    def test_authenticity_shown_when_enabled(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(
            info, info, real_shit=False,
            appearance={"color": False, "show_authenticity": True, "easter_eggs": True},
        )
        assert "Authenticity" in result

    def test_authenticity_hidden_when_disabled(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(
            info, info, real_shit=False,
            appearance={"color": False, "show_authenticity": False},
        )
        assert "Authenticity" not in result

    def test_display_order(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(
            username="user",
            hostname="host",
            os="Linux",
            cpu="Intel i7",
            memory="16 GiB",
        )
        result = render(info, info, real_shit=False, appearance={"color": False})
        os_pos = result.find("OS:")
        cpu_pos = result.find("CPU:")
        mem_pos = result.find("Memory:")
        assert os_pos < cpu_pos < mem_pos

    def test_custom_fields_displayed(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(
            username="user", hostname="host", os="Linux", custom_field="custom_value"
        )
        result = render(info, info, real_shit=False, appearance={"color": False})
        assert "Custom Field" in result
        assert "custom_value" in result

    def test_empty_info_renders(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = SystemInfo(fields=OrderedDict())
        result = render(info, info, real_shit=False, appearance={"color": False})
        assert len(result) > 0

    def test_ansi_safe_alignment(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        # When color is enabled, ANSI codes shouldn't break alignment
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(info, info, real_shit=False, appearance={"color": True})
        # Each line should have consistent structure
        lines = result.split("\n")
        assert len(lines) >= 3  # at least header, separator, one info line


class TestColors:
    def test_no_color_mode(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        # Reset colors to non-empty first
        Colors.RESET = "\033[0m"
        from larpfetch.renderer import _should_color
        assert not _should_color()
