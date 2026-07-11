"""Tests for the resolver module."""

from collections import OrderedDict

from larpfetch.models import SystemInfo
from larpfetch.resolver import (
    SOURCE_CLI,
    SOURCE_DEFAULT,
    SOURCE_PROFILE,
    SOURCE_REAL,
    resolve,
    resolve_with_sources,
)


def _make_info(**kwargs: str) -> SystemInfo:
    return SystemInfo(fields=OrderedDict(kwargs))


class TestResolver:
    def test_real_shit_returns_real_values(self):
        real = _make_info(os="Linux", cpu="Real CPU", memory="16 GiB")
        default = {"os": "Arch Linux", "cpu": "AMD Ryzen 9"}
        selected = {"os": "Windows 11 Pro"}
        cli = {"memory": "69 PiB"}

        result = resolve(real, default, selected, cli, real_shit=True)

        assert result.get("os") == "Linux"
        assert result.get("cpu") == "Real CPU"
        assert result.get("memory") == "16 GiB"

    def test_real_shit_ignores_default_profile(self):
        real = _make_info(os="Linux")
        default = {"os": "Arch Linux", "cpu": "AMD Ryzen 9"}

        result = resolve(real, default, None, {}, real_shit=True)

        assert result.get("os") == "Linux"
        assert result.get("cpu") == ""  # not overridden by default

    def test_real_shit_ignores_selected_profile(self):
        real = _make_info(os="Linux")
        default = {"os": "Arch Linux"}
        selected = {"os": "Windows 11 Pro", "kernel": "6.99.0-larp"}

        result = resolve(real, default, selected, {}, real_shit=True)

        assert result.get("os") == "Linux"
        assert result.get("kernel") == ""  # not overridden

    def test_real_shit_ignores_cli_overrides(self):
        real = _make_info(os="Linux")
        default = {"os": "Arch Linux"}
        cli = {"os": "macOS 14.0", "cpu": "Apple M7 Ultra"}

        result = resolve(real, default, None, cli, real_shit=True)

        assert result.get("os") == "Linux"
        assert result.get("cpu") == ""  # not overridden

    def test_default_profile_overrides_real(self):
        real = _make_info(os="Linux", cpu="Intel Core i7")
        default = {"os": "Arch Linux", "kernel": "6.99.0-larp"}

        result = resolve(real, default, None, {})

        assert result.get("os") == "Arch Linux"
        assert result.get("kernel") == "6.99.0-larp"
        assert result.get("cpu") == "Intel Core i7"  # real, not overridden

    def test_selected_profile_overrides_default(self):
        real = _make_info(os="Linux", cpu="Intel Core i7")
        default = {"os": "Arch Linux", "kernel": "6.99.0-larp"}
        selected = {"os": "Windows 11 Pro"}

        result = resolve(real, default, selected, {})

        assert result.get("os") == "Windows 11 Pro"
        assert result.get("kernel") == "6.99.0-larp"  # from default
        assert result.get("cpu") == "Intel Core i7"  # from real

    def test_selected_profile_inherits_from_default(self):
        real = _make_info(os="Linux")
        default = {"os": "Arch Linux", "kernel": "6.99.0-larp"}
        selected = {"cpu": "Quantum Potato 9000"}  # no os override

        result = resolve(real, default, selected, {})

        assert result.get("os") == "Arch Linux"  # from default
        assert result.get("kernel") == "6.99.0-larp"  # from default
        assert result.get("cpu") == "Quantum Potato 9000"  # from selected

    def test_cli_overrides_everything(self):
        real = _make_info(os="Linux", cpu="Intel Core i7")
        default = {"os": "Arch Linux", "kernel": "6.99.0-larp"}
        selected = {"os": "Windows 11 Pro"}
        cli = {"os": "macOS 14.0", "cpu": "Apple M7 Ultra"}

        result = resolve(real, default, selected, cli)

        assert result.get("os") == "macOS 14.0"
        assert result.get("cpu") == "Apple M7 Ultra"
        assert result.get("kernel") == "6.99.0-larp"  # from default

    def test_full_precedence_chain(self):
        real = _make_info(
            os="Linux",
            hostname="real-host",
            cpu="Intel Core i7",
            memory="16 GiB",
            kernel="5.15.0",
        )
        default = {
            "os": "Arch Linux",
            "hostname": "btw-i-use-arch",
            "cpu": "AMD Ryzen 9",
        }
        selected = {
            "os": "Windows 11 Pro",
            "hostname": "mainframe-01",
        }
        cli = {"os": "macOS 14.0"}

        result = resolve(real, default, selected, cli)

        assert result.get("os") == "macOS 14.0"  # CLI wins
        assert result.get("hostname") == "mainframe-01"  # selected wins
        assert result.get("cpu") == "AMD Ryzen 9"  # default wins
        assert result.get("memory") == "16 GiB"  # real
        assert result.get("kernel") == "5.15.0"  # real

    def test_empty_overrides_preserve_real(self):
        real = _make_info(os="Linux")
        result = resolve(real, {}, None, {})
        assert result.get("os") == "Linux"

    def test_impossible_combination_accepted(self):
        real = _make_info(os="Linux")
        default = {
            "os": "Windows 11 Pro",
            "kernel": "6.18.7-arch1-1",
            "cpu": "Apple M7 Ultra",
            "gpu": "NVIDIA RTX 9090 Ti",
            "memory": "69 PiB",
            "shell": "HolyC",
            "de": "GNOME 83",
            "package_manager": "apt btw",
        }

        result = resolve(real, default, None, {})

        assert result.get("os") == "Windows 11 Pro"
        assert result.get("kernel") == "6.18.7-arch1-1"
        assert result.get("cpu") == "Apple M7 Ultra"
        assert result.get("gpu") == "NVIDIA RTX 9090 Ti"
        assert result.get("memory") == "69 PiB"
        assert result.get("shell") == "HolyC"
        assert result.get("de") == "GNOME 83"
        assert result.get("package_manager") == "apt btw"

    def test_arbitrary_custom_fields(self):
        real = _make_info(os="Linux")
        default = {"os": "Arch Linux", "custom_field": "custom_value"}

        result = resolve(real, default, None, {})

        assert result.get("custom_field") == "custom_value"

    def test_empty_string_override_not_applied(self):
        real = _make_info(os="Linux")
        default = {"os": ""}  # empty strings should not override

        result = resolve(real, default, None, {})
        assert result.get("os") == "Linux"

    def test_none_selected_profile(self):
        real = _make_info(os="Linux")
        result = resolve(real, {"os": "Arch"}, None, {})
        assert result.get("os") == "Arch"


class TestResolveWithSources:
    def test_real_source(self):
        real = _make_info(os="Linux", cpu="Intel")
        _, sources = resolve_with_sources(real, {}, None, {})
        assert sources["os"] == SOURCE_REAL
        assert sources["cpu"] == SOURCE_REAL

    def test_default_source(self):
        real = _make_info(os="Linux")
        _, sources = resolve_with_sources(real, {"os": "Arch"}, None, {})
        assert sources["os"] == SOURCE_DEFAULT

    def test_profile_source(self):
        real = _make_info(os="Linux")
        _, sources = resolve_with_sources(
            real, {"os": "Arch"}, {"os": "Windows"}, {}
        )
        assert sources["os"] == SOURCE_PROFILE

    def test_cli_source(self):
        real = _make_info(os="Linux")
        _, sources = resolve_with_sources(
            real, {"os": "Arch"}, {"os": "Windows"}, {"os": "macOS"}
        )
        assert sources["os"] == SOURCE_CLI

    def test_mixed_sources(self):
        real = _make_info(os="Linux", cpu="Intel", memory="16 GiB")
        resolved, sources = resolve_with_sources(
            real,
            {"os": "Arch"},
            {"cpu": "Ryzen"},
            {"memory": "69 PiB"},
        )
        assert sources["os"] == SOURCE_DEFAULT
        assert sources["cpu"] == SOURCE_PROFILE
        assert sources["memory"] == SOURCE_CLI
        assert resolved.get("os") == "Arch"

    def test_real_shit_all_real(self):
        real = _make_info(os="Linux", cpu="Intel")
        resolved, sources = resolve_with_sources(
            real,
            {"os": "Arch"},
            {"cpu": "Ryzen"},
            {"memory": "69 PiB"},
            real_shit=True,
        )
        assert sources["os"] == SOURCE_REAL
        assert sources["cpu"] == SOURCE_REAL
        assert "memory" not in resolved.fields
        assert resolved.get("os") == "Linux"

    def test_resolve_matches_resolve_with_sources(self):
        real = _make_info(os="Linux", cpu="Intel")
        default = {"os": "Arch"}
        selected = {"cpu": "Ryzen"}
        cli = {"memory": "69 PiB"}
        a = resolve(real, default, selected, cli)
        b, _ = resolve_with_sources(real, default, selected, cli)
        assert a.to_dict() == b.to_dict()
