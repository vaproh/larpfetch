"""Tests for easter eggs module."""

from collections import OrderedDict

from larpfetch.easter_eggs import (
    _compute_authenticity,
    _is_implausible_memory,
    get_authenticity_line,
    get_extra_lines,
)
from larpfetch.models import SystemInfo


def _make_info(**kwargs: str) -> SystemInfo:
    return SystemInfo(fields=OrderedDict(kwargs))


class TestImplausibleMemory:
    def test_normal_memory_not_implausible(self):
        assert not _is_implausible_memory("8 GiB")
        assert not _is_implausible_memory("16 GiB")
        assert not _is_implausible_memory("512 GiB")

    def test_tib_implausible(self):
        assert _is_implausible_memory("1 TiB")
        assert _is_implausible_memory("2 TiB")

    def test_pib_implausible(self):
        assert _is_implausible_memory("69 PiB")
        assert _is_implausible_memory("1 PiB")

    def test_eib_implausible(self):
        assert _is_implausible_memory("1 EiB")

    def test_empty_string(self):
        assert not _is_implausible_memory("")

    def test_no_number(self):
        assert not _is_implausible_memory("Unknown")

    def test_sub_tiB_not_implausible(self):
        assert not _is_implausible_memory("999 GiB")


class TestAuthenticity:
    def test_real_shit_100_percent(self):
        real = _make_info(os="Linux")
        result = _compute_authenticity(real, real, real_shit=True)
        assert result == 100

    def test_identical_info_high_authenticity(self):
        real = _make_info(os="Linux", cpu="Intel")
        resolved = _make_info(os="Linux", cpu="Intel")
        result = _compute_authenticity(real, resolved, real_shit=False)
        assert result == 100

    def test_different_info_low_authenticity(self):
        real = _make_info(os="Linux", cpu="Intel")
        resolved = _make_info(os="Windows", cpu="AMD")
        result = _compute_authenticity(real, resolved, real_shit=False)
        assert result == 0

    def test_partial_match(self):
        real = _make_info(os="Linux", cpu="Intel", memory="16 GiB")
        resolved = _make_info(os="Linux", cpu="AMD", memory="16 GiB")
        result = _compute_authenticity(real, resolved, real_shit=False)
        assert 0 < result < 100


class TestAuthenticityLine:
    def test_real_shit_shows_100(self):
        real = _make_info(os="Linux")
        line = get_authenticity_line(real, real, real_shit=True, easter_eggs=True)
        assert line is not None
        assert "100%" in line

    def test_disabled_when_no_easter_eggs(self):
        real = _make_info(os="Linux")
        line = get_authenticity_line(real, real, real_shit=True, easter_eggs=False)
        assert line is None

    def test_disabled_via_env_var(self, monkeypatch):
        monkeypatch.setenv("LARPFETCH_NO_EASTER_EGGS", "1")
        real = _make_info(os="Linux")
        line = get_authenticity_line(real, real, real_shit=True, easter_eggs=True)
        assert line is None


class TestExtraLines:
    def test_real_shit_source_reality(self):
        real = _make_info(os="Linux")
        lines = get_extra_lines(real, real, real_shit=True, easter_eggs=True)
        assert any("reality" in line.lower() for line in lines)

    def test_real_shit_disappointment(self):
        real = _make_info(os="Linux")
        lines = get_extra_lines(real, real, real_shit=True, easter_eggs=True)
        assert any("disappointment" in line.lower() for line in lines)

    def test_implausible_memory_trust_me(self):
        resolved = _make_info(memory="69 PiB")
        real = _make_info()
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=True)
        assert any("trust me bro" in line.lower() for line in lines)

    def test_high_package_count_leakage(self):
        resolved = _make_info(package_count="100000")
        real = _make_info()
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=True)
        assert any("leakage" in line.lower() for line in lines)

    def test_disabled_when_no_easter_eggs(self):
        resolved = _make_info(memory="69 PiB")
        real = _make_info()
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=False)
        assert lines == []

    def test_disabled_via_env_var(self, monkeypatch):
        monkeypatch.setenv("LARPFETCH_NO_EASTER_EGGS", "1")
        resolved = _make_info(memory="69 PiB")
        real = _make_info()
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=True)
        assert lines == []

    def test_deterministic_allegations(self):
        # Same username should produce same result every time
        info = _make_info(username="testuser123")
        real = _make_info()
        lines1 = get_extra_lines(info, real, real_shit=False, easter_eggs=True)
        lines2 = get_extra_lines(info, real, real_shit=False, easter_eggs=True)
        assert lines1 == lines2

    def test_out_larp_when_real_is_implausible(self):
        real = _make_info(memory="2 TiB")
        resolved = _make_info(memory="8 GiB")
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=True)
        assert any("out-larped" in line.lower() for line in lines)

    def test_no_out_larp_when_real_is_normal(self):
        real = _make_info(memory="8 GiB")
        resolved = _make_info(memory="69 PiB")
        lines = get_extra_lines(resolved, real, real_shit=False, easter_eggs=True)
        assert not any("out-larped" in line.lower() for line in lines)
