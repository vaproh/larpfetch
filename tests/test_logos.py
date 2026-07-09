"""Tests for logos module."""

from larpfetch.logos import (
    LOGO_ART,
    LOGO_COLORS,
    _normalize,
    get_logo_height,
    get_logo_width,
    select_logo,
)


class TestSelectLogo:
    def test_arch_linux_selects_arch(self):
        art, colors = select_logo("Arch Linux")
        assert art == LOGO_ART["arch"]

    def test_ubuntu_selects_ubuntu(self):
        art, colors = select_logo("Ubuntu 22.04")
        assert art == LOGO_ART["ubuntu"]

    def test_debian_selects_debian(self):
        art, colors = select_logo("Debian GNU/Linux")
        assert art == LOGO_ART["debian"]

    def test_fedora_selects_fedora(self):
        art, colors = select_logo("Fedora Linux 39")
        assert art == LOGO_ART["fedora"]

    def test_windows_selects_windows(self):
        art, colors = select_logo("Windows 11 Pro")
        assert art == LOGO_ART["windows"]

    def test_macos_selects_macos(self):
        art, colors = select_logo("macOS 14.0")
        assert art == LOGO_ART["macos"]

    def test_darwin_selects_macos(self):
        art, colors = select_logo("Darwin 23.0.0")
        assert art == LOGO_ART["macos"]

    def test_templeos_selects_templeos(self):
        art, colors = select_logo("TempleOS")
        assert art == LOGO_ART["templeos"]

    def test_nasa_selects_nasa(self):
        art, colors = select_logo("NASA Linux")
        assert art == LOGO_ART["nasa"]

    def test_haiku_selects_haiku(self):
        art, colors = select_logo("Haiku OS")
        assert art == LOGO_ART["haiku"]

    def test_unknown_selects_unknown(self):
        art, colors = select_logo("Some Random OS")
        assert art == LOGO_ART["unknown"]

    def test_empty_string_selects_unknown(self):
        art, colors = select_logo("")
        assert art == LOGO_ART["unknown"]

    def test_case_insensitive(self):
        assert select_logo("ARCH LINUX")[0] == LOGO_ART["arch"]
        assert select_logo("windows")[0] == LOGO_ART["windows"]
        assert select_logo("MACOS")[0] == LOGO_ART["macos"]

    def test_whitespace_handling(self):
        assert select_logo("  Arch Linux  ")[0] == LOGO_ART["arch"]

    def test_returns_colors(self):
        _, colors = select_logo("Arch Linux")
        assert isinstance(colors, list)
        assert len(colors) > 0

    def test_returns_colors_for_fedora(self):
        _, colors = select_logo("Fedora Linux")
        assert len(colors) >= 2


class TestLogoDimensions:
    def test_all_logos_have_consistent_width(self):
        for name, logo in LOGO_ART.items():
            assert len(logo) > 0, f"Logo '{name}' is empty"
            widths = [len(line) for line in logo]
            max_w = max(widths)
            # No logo line should be absurdly wide
            assert max_w <= 100, f"Logo '{name}' has a line wider than 100 chars: {max_w}"

    def test_get_logo_height(self):
        assert get_logo_height(LOGO_ART["arch"]) == len(LOGO_ART["arch"])

    def test_get_logo_width(self):
        assert get_logo_width(LOGO_ART["arch"]) == max(len(line) for line in LOGO_ART["arch"])

    def test_all_logos_positive_height(self):
        for name, logo in LOGO_ART.items():
            assert get_logo_height(logo) > 0, f"Logo '{name}' has no height"
            assert get_logo_width(logo) > 0, f"Logo '{name}' has no width"

    def test_all_logos_have_color_arrays(self):
        for name in LOGO_ART:
            assert name in LOGO_COLORS, f"Logo '{name}' missing from LOGO_COLORS"


class TestNormalize:
    def test_direct_match(self):
        assert _normalize("arch") == "arch"
        assert _normalize("parrot") == "parrot"

    def test_substring_match(self):
        assert _normalize("Parrot Security OS") == "parrot"
        assert _normalize("Arch Linux") == "arch"
        assert _normalize("NixOS 24.05") == "nixos"

    def test_fallback_to_unknown(self):
        assert _normalize("Something Weird") == "unknown"

    def test_profile_name_match(self):
        # Profile names like "nasa" should match
        assert _normalize("nasa") == "nasa"
        assert _normalize("haiku") == "haiku"
