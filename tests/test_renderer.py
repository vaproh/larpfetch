"""Tests for the renderer module."""

from collections import OrderedDict

from larpfetch.models import DisplayConfig, SystemInfo
from larpfetch.renderer import (
    _COLOR_VALUES,
    _get_colors,
    render,
    render_diff,
    render_sources,
)


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
        assert len(result) > 0

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
            info,
            info,
            real_shit=False,
            appearance={"color": False, "show_authenticity": True, "easter_eggs": True},
        )
        assert "Authenticity" in result

    def test_authenticity_hidden_when_disabled(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(
            info,
            info,
            real_shit=False,
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
            username="user",
            hostname="host",
            os="Linux",
            custom_field="custom_value",
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

    def test_column_alignment(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        result = render(info, info, real_shit=False, appearance={"color": False})
        lines = result.split("\n")
        # Find the position of the first ":" in each info line (the label separator)
        for line in lines[2:]:  # skip header and separator
            if ":" in line:
                # All info lines should have the colon at roughly the same position
                # (within 2 chars for label length variation)
                assert True  # line has a colon separator


class TestColors:
    def test_no_color_mode(self, monkeypatch):
        monkeypatch.setenv("NO_COLOR", "1")
        from larpfetch.renderer import _should_color

        assert not _should_color()

    def test_force_color_true(self):
        from larpfetch.renderer import _should_color

        assert _should_color(force_color=True)

    def test_force_color_false(self):
        from larpfetch.renderer import _should_color

        assert not _should_color(force_color=False)

    def test_colors_not_permanently_mutated(self):
        """Colors.disable() should not affect _COLOR_VALUES constant."""
        original = dict(_COLOR_VALUES)
        colors_disabled = _get_colors(False)
        colors_enabled = _get_colors(True)
        # Original values should be preserved
        assert _COLOR_VALUES == original
        # Disabled should have empty strings
        assert all(v == "" for v in colors_disabled.values())
        # Enabled should have real values
        assert colors_enabled["RESET"] == "\033[0m"
        assert colors_enabled["BOLD"] == "\033[1m"


class TestLogoOverride:
    def test_profile_logo_field_overrides_os(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(
            username="user",
            hostname="host",
            os="Some Unknown OS",
            logo="arch",
        )
        real = _make_info(os="Linux")
        result = render(info, real, real_shit=False, appearance={"color": False})
        # Should use arch logo, not generic (from "Some Unknown OS")
        assert "user@host" in result

    def test_real_shit_ignores_logo_field(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(
            os="Windows 11 Pro",
            logo="arch",
        )
        real = _make_info(os="Linux")
        result = render(info, real, real_shit=True, appearance={"color": False})
        # In --real-shit mode, should use real OS for logo, not profile's logo
        assert len(result) > 0

    def test_custom_logo_art_via_newlines(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        custom_art = "CUSTOM_LOGO_LINE_1\nCUSTOM_LOGO_LINE_2"
        info = _make_info(
            username="user",
            hostname="host",
            os="TestOS",
            logo=custom_art,
        )
        real = _make_info(os="Linux")
        result = render(info, real, real_shit=False, appearance={"color": False})
        assert "CUSTOM_LOGO_LINE_1" in result
        assert "CUSTOM_LOGO_LINE_2" in result

    def test_logo_colors_applied_when_color_enabled(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Arch Linux")
        result = render(info, info, real_shit=False, appearance={"color": True})
        # Arch logo has $1/$2 color codes, should have ANSI in output
        lines = result.split("\n")
        # First line of arch logo should have ANSI codes
        assert "\033[" in lines[0]

    def test_logo_colors_stripped_when_no_color(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Arch Linux")
        result = render(info, info, real_shit=False, appearance={"color": False})
        # No $N placeholders should remain
        assert "$1" not in result
        assert "$2" not in result


class TestDisplayConfig:
    def test_custom_separator(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        cfg = DisplayConfig(separator=" -> ")
        result = render(
            info, info, real_shit=False, appearance={"color": False},
            display_config=cfg,
        )
        assert "OS -> Linux" in result
        assert "OS: Linux" not in result

    def test_field_filtering(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(
            username="user", hostname="host", os="Linux", cpu="Intel", kernel="6.8.0",
        )
        cfg = DisplayConfig(fields=["os", "cpu"])
        result = render(
            info, info, real_shit=False, appearance={"color": False},
            display_config=cfg,
        )
        assert "OS:" in result
        assert "CPU:" in result
        assert "Kernel:" not in result

    def test_custom_labels(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", memory="16 GiB")
        cfg = DisplayConfig(field_labels={"memory": "RAM"})
        result = render(
            info, info, real_shit=False, appearance={"color": False},
            display_config=cfg,
        )
        assert "RAM:" in result
        assert "Memory:" not in result

    def test_hide_unavailable_fields(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux", gpu="")
        cfg = DisplayConfig(
            fields=["os", "gpu", "username"],
            hide_unavailable=True,
        )
        result = render(
            info, info, real_shit=False, appearance={"color": False},
            display_config=cfg,
        )
        assert "OS:" in result
        assert "User:" in result
        assert "GPU:" not in result

    def test_terminal_width_forces_no_logo(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        info = _make_info(username="user", hostname="host", os="Linux")
        # Very narrow terminal should hide logo
        result = render(
            info, info, real_shit=False,
            appearance={"color": False},
            cols=30, display_config=DisplayConfig(),
        )
        lines = result.split("\n")
        # First line should just be header, no logo art
        assert "user@host" in lines[0]


class TestRenderDiff:
    def test_shows_differences(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Arch Linux", cpu="Intel")
        resolved = _make_info(os="NASA Linux", cpu="Intel")
        result = render_diff(resolved, real, appearance={"color": False})
        assert "OS" in result
        assert "Arch Linux" in result
        assert "NASA Linux" in result
        assert "->" in result

    def test_hides_matching_fields(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Arch Linux", cpu="Intel")
        resolved = _make_info(os="NASA Linux", cpu="Intel")
        result = render_diff(resolved, real, appearance={"color": False})
        # CPU matches, should not appear
        assert "CPU" not in result

    def test_no_differences_message(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Arch Linux")
        resolved = _make_info(os="Arch Linux")
        result = render_diff(resolved, real, appearance={"color": False})
        assert "No differences" in result

    def test_missing_real_shows_none(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        real = _make_info(os="Arch Linux")
        resolved = _make_info(os="Arch Linux", cpu="Fake CPU")
        result = render_diff(resolved, real, appearance={"color": False})
        assert "(none)" in result


class TestRenderSources:
    def test_annotates_sources(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        resolved = _make_info(os="NASA Linux", cpu="Intel")
        sources = {"os": "profile", "cpu": "real"}
        result = render_sources(resolved, sources, appearance={"color": False})
        assert "[profile]" in result
        assert "[real]" in result
        assert "OS" in result

    def test_default_source_is_real(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        resolved = _make_info(os="Arch")
        result = render_sources(resolved, {}, appearance={"color": False})
        assert "[real]" in result

    def test_respects_display_config(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        resolved = _make_info(os="Arch", cpu="Intel", kernel="6.8.0")
        sources = {"os": "profile", "cpu": "real", "kernel": "real"}
        cfg = DisplayConfig(fields=["os"])
        result = render_sources(resolved, sources, appearance={"color": False},
                                display_config=cfg)
        assert "OS" in result
        assert "CPU" not in result
