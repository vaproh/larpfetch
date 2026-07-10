"""Tests for the config module."""

from pathlib import Path

import pytest

from larpfetch.config import (
    get_appearance,
    get_default_profile,
    get_display_config,
    get_named_profiles,
    load_config,
)


class TestLoadConfig:
    def test_no_config_returns_defaults(self, monkeypatch):
        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        config = load_config()
        assert config["default"] == {}
        assert config["profiles"] == {}
        assert config["appearance"] == {}

    def test_load_valid_config(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[default]
os = "Arch Linux"
kernel = "6.99.0-larp"

[profiles.nasa]
os = "NASA Linux"
cpu = "Quantum Potato 9000"

[profiles.abomination]
os = "Windows 11 Pro"
kernel = "6.18.7-arch1-1"

[appearance]
color = true
show_authenticity = true
"""
        )
        config = load_config(str(config_file))
        assert config["default"]["os"] == "Arch Linux"
        assert config["profiles"]["nasa"]["os"] == "NASA Linux"
        assert config["profiles"]["abomination"]["kernel"] == "6.18.7-arch1-1"
        assert config["appearance"]["color"] is True

    def test_missing_file_raises_error(self):
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config("/nonexistent/path/config.toml")

    def test_malformed_toml_raises_error(self, tmp_path):
        config_file = tmp_path / "bad.toml"
        config_file.write_text("this is not [valid toml {{{")
        with pytest.raises(Exception):
            load_config(str(config_file))

    def test_empty_config_file(self, tmp_path):
        config_file = tmp_path / "empty.toml"
        config_file.write_text("")
        config = load_config(str(config_file))
        assert config["default"] == {}
        assert config["profiles"] == {}

    def test_unknown_fields_allowed(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[default]
os = "Arch Linux"
custom_thing = "yes"
another_custom = 42

[profiles.test]
os = "Test"
banana = "yellow"
"""
        )
        config = load_config(str(config_file))
        assert config["default"]["custom_thing"] == "yes"
        assert config["default"]["another_custom"] == 42
        assert config["profiles"]["test"]["banana"] == "yellow"


class TestGetDefaultProfile:
    def test_returns_string_dict(self):
        config = {"default": {"os": "Linux", "kernel": "5.15.0"}}
        result = get_default_profile(config)
        assert result == {"os": "Linux", "kernel": "5.15.0"}

    def test_empty_default(self):
        config = {}
        result = get_default_profile(config)
        assert result == {}


class TestGetNamedProfiles:
    def test_returns_string_dict(self):
        config = {
            "profiles": {
                "nasa": {"os": "NASA Linux", "cpu": "Quantum Potato 9000"},
                "test": {"os": "Test"},
            }
        }
        result = get_named_profiles(config)
        assert "nasa" in result
        assert "test" in result
        assert result["nasa"]["os"] == "NASA Linux"

    def test_empty_profiles(self):
        config = {}
        result = get_named_profiles(config)
        assert result == {}


class TestGetAppearance:
    def test_returns_appearance(self):
        config = {"appearance": {"color": True, "show_authenticity": True}}
        result = get_appearance(config)
        assert result["color"] is True

    def test_empty_appearance(self):
        config = {}
        result = get_appearance(config)
        assert result == {}


class TestGetDisplayConfig:
    def test_no_display_section_returns_defaults(self):
        config = {}
        dc = get_display_config(config)
        assert dc.fields is None
        assert dc.field_labels is None
        assert dc.separator == ": "
        assert dc.hide_unavailable is False

    def test_fields_from_config(self):
        config = {"display": {"fields": ["os", "kernel", "cpu"]}}
        dc = get_display_config(config)
        assert dc.fields == ["os", "kernel", "cpu"]

    def test_labels_from_config(self):
        config = {"display": {"labels": {"memory": "RAM", "packages": "Pkgs"}}}
        dc = get_display_config(config)
        assert dc.field_labels["memory"] == "RAM"
        assert dc.field_labels["packages"] == "Pkgs"

    def test_separator(self):
        config = {"display": {"separator": " -> "}}
        dc = get_display_config(config)
        assert dc.separator == " -> "

    def test_hide_unavailable(self):
        config = {"display": {"hide_unavailable": True}}
        dc = get_display_config(config)
        assert dc.hide_unavailable is True

    def test_display_section_in_full_config(self, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[default]
os = "Arch Linux"

[display]
fields = ["os", "kernel"]
separator = " :: "

[display.labels]
memory = "RAM"
""")
        config = load_config(str(config_file))
        dc = get_display_config(config)
        assert dc.fields == ["os", "kernel"]
        assert dc.separator == " :: "
        assert dc.field_labels["memory"] == "RAM"
