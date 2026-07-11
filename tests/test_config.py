"""Tests for the config module."""

from pathlib import Path

import pytest

from larpfetch.config import (
    export_profile_toml,
    get_appearance,
    get_default_profile,
    get_display_config,
    get_named_profiles,
    load_config,
    load_profile_file,
    validate_config,
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


class TestLoadProfileFile:
    def test_flat_format(self, tmp_path):
        f = tmp_path / "p.toml"
        f.write_text('os = "Arch Linux"\ncpu = "Ryzen"\nlogo = "arch"\n')
        result = load_profile_file(str(f))
        assert result == {"os": "Arch Linux", "cpu": "Ryzen", "logo": "arch"}

    def test_profile_table_format(self, tmp_path):
        f = tmp_path / "p.toml"
        f.write_text('[profile]\nos = "NASA Linux"\ncpu = "Quantum Potato"\n')
        result = load_profile_file(str(f))
        assert result == {"os": "NASA Linux", "cpu": "Quantum Potato"}

    def test_ignores_nested_tables_in_flat(self, tmp_path):
        f = tmp_path / "p.toml"
        f.write_text('os = "Arch"\n[extra]\nx = "y"\n')
        result = load_profile_file(str(f))
        assert result == {"os": "Arch"}

    def test_coerces_to_string(self, tmp_path):
        f = tmp_path / "p.toml"
        f.write_text("count = 42\n")
        result = load_profile_file(str(f))
        assert result == {"count": "42"}

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_profile_file("/nonexistent/profile.toml")


class TestExportProfileToml:
    def test_basic_export(self):
        text = export_profile_toml({"os": "Arch Linux", "cpu": "Ryzen"})
        assert 'os = "Arch Linux"' in text
        assert 'cpu = "Ryzen"' in text

    def test_roundtrip(self, tmp_path):
        fields = {"os": "Arch Linux", "cpu": "Ryzen", "kernel": "6.8.0"}
        text = export_profile_toml(fields)
        f = tmp_path / "out.toml"
        f.write_text(text)
        loaded = load_profile_file(str(f))
        for k, v in fields.items():
            assert loaded[k] == v

    def test_escapes_quotes(self, tmp_path):
        fields = {"os": 'Weird "Quoted" OS'}
        text = export_profile_toml(fields)
        f = tmp_path / "out.toml"
        f.write_text(text)
        loaded = load_profile_file(str(f))
        assert loaded["os"] == 'Weird "Quoted" OS'

    def test_name_included_as_comment(self):
        text = export_profile_toml({"os": "Arch"}, name="myrig")
        assert "myrig" in text

    def test_known_fields_ordered_first(self):
        text = export_profile_toml({"zzz_custom": "x", "os": "Arch"})
        assert text.index('os =') < text.index('zzz_custom =')


class TestValidateConfig:
    def test_valid_config(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[default]\nos = "Arch"\n[appearance]\ncolor = true\n')
        errors, warnings = validate_config(str(f))
        assert errors == []

    def test_unknown_section_warns(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[bogus]\nx = 1\n')
        errors, warnings = validate_config(str(f))
        assert any("bogus" in w for w in warnings)

    def test_unknown_appearance_key_warns(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[appearance]\nbogus = true\n')
        errors, warnings = validate_config(str(f))
        assert any("bogus" in w for w in warnings)

    def test_non_bool_appearance_errors(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[appearance]\ncolor = "yes"\n')
        errors, warnings = validate_config(str(f))
        assert any("color" in e for e in errors)

    def test_display_fields_must_be_list(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[display]\nfields = "os"\n')
        errors, warnings = validate_config(str(f))
        assert any("display.fields" in e for e in errors)

    def test_unknown_display_field_warns(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[display]\nfields = ["os", "nonsense"]\n')
        errors, warnings = validate_config(str(f))
        assert any("nonsense" in w for w in warnings)

    def test_aliases_accepted_in_display_fields(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[display]\nfields = ["host", "ram"]\n')
        errors, warnings = validate_config(str(f))
        assert not any("host" in w or "ram" in w for w in warnings)

    def test_bad_separator_errors(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[display]\nseparator = 5\n')
        errors, warnings = validate_config(str(f))
        assert any("separator" in e for e in errors)

    def test_invalid_toml_errors(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text("this is [not valid {{{")
        errors, warnings = validate_config(str(f))
        assert any("TOML" in e for e in errors)

    def test_missing_explicit_path_raises(self):
        with pytest.raises(FileNotFoundError):
            validate_config("/nonexistent/config.toml")

    def test_no_config_warns(self, monkeypatch):
        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        errors, warnings = validate_config()
        assert errors == []
        assert len(warnings) >= 1
