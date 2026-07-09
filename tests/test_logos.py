"""Tests for logos module."""

from larpfetch.logos import LOGOS, get_logo_height, get_logo_width, select_logo


class TestSelectLogo:
    def test_arch_linux_selects_arch(self):
        logo = select_logo("Arch Linux")
        assert logo == LOGOS["arch"]

    def test_ubuntu_selects_ubuntu(self):
        logo = select_logo("Ubuntu 22.04")
        assert logo == LOGOS["ubuntu"]

    def test_debian_selects_debian(self):
        logo = select_logo("Debian GNU/Linux")
        assert logo == LOGOS["debian"]

    def test_fedora_selects_fedora(self):
        logo = select_logo("Fedora Linux 39")
        assert logo == LOGOS["fedora"]

    def test_windows_selects_windows(self):
        logo = select_logo("Windows 11 Pro")
        assert logo == LOGOS["windows"]

    def test_macos_selects_macos(self):
        logo = select_logo("macOS 14.0")
        assert logo == LOGOS["macos"]

    def test_darwin_selects_macos(self):
        logo = select_logo("Darwin 23.0.0")
        assert logo == LOGOS["macos"]

    def test_templeos_selects_templeos(self):
        logo = select_logo("TempleOS")
        assert logo == LOGOS["templeos"]

    def test_nasa_selects_nasa(self):
        logo = select_logo("NASA Linux")
        assert logo == LOGOS["nasa"]

    def test_haiku_selects_haiku(self):
        logo = select_logo("Haiku OS")
        assert logo == LOGOS["haiku"]

    def test_unknown_selects_generic(self):
        logo = select_logo("Some Random OS")
        assert logo == LOGOS["generic"]

    def test_empty_string_selects_generic(self):
        logo = select_logo("")
        assert logo == LOGOS["generic"]

    def test_case_insensitive(self):
        assert select_logo("ARCH LINUX") == LOGOS["arch"]
        assert select_logo("windows") == LOGOS["windows"]
        assert select_logo("MACOS") == LOGOS["macos"]

    def test_whitespace_handling(self):
        assert select_logo("  Arch Linux  ") == LOGOS["arch"]


class TestLogoDimensions:
    def test_all_logos_have_consistent_width(self):
        for name, logo in LOGOS.items():
            assert len(logo) > 0, f"Logo '{name}' is empty"
            widths = [len(line) for line in logo]
            max_w = max(widths)
            # No logo line should be absurdly wide
            assert max_w <= 100, f"Logo '{name}' has a line wider than 100 chars: {max_w}"

    def test_get_logo_height(self):
        assert get_logo_height(LOGOS["arch"]) == len(LOGOS["arch"])

    def test_get_logo_width(self):
        assert get_logo_width(LOGOS["arch"]) == max(len(line) for line in LOGOS["arch"])

    def test_all_logos_positive_height(self):
        for name, logo in LOGOS.items():
            assert get_logo_height(logo) > 0, f"Logo '{name}' has no height"
            assert get_logo_width(logo) > 0, f"Logo '{name}' has no width"


class TestNormalize:
    def test_direct_match(self):
        from larpfetch.logos import _normalize
        assert _normalize("arch") == "arch"
        assert _normalize("parrot") == "parrot"

    def test_substring_match(self):
        from larpfetch.logos import _normalize
        assert _normalize("Parrot Security OS") == "parrot"
        assert _normalize("Arch Linux") == "arch"
        assert _normalize("NixOS 24.05") == "nixos"

    def test_fallback_to_generic(self):
        from larpfetch.logos import _normalize
        assert _normalize("Something Weird") == "generic"
