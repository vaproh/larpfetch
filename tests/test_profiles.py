"""Tests for built-in profiles."""

from larpfetch.profiles import (
    BUILTIN_PROFILES,
    get_builtin_profile_names,
    get_builtin_profiles,
)


class TestBuiltinProfiles:
    def test_all_profiles_have_os(self):
        for name, profile in BUILTIN_PROFILES.items():
            assert "os" in profile, f"Profile '{name}' missing 'os'"

    def test_all_profiles_are_strings(self):
        profiles = get_builtin_profiles()
        for name, profile in profiles.items():
            for k, v in profile.items():
                assert isinstance(v, str), f"Profile '{name}' field '{k}' is not a string"

    def test_profile_names_sorted(self):
        names = get_builtin_profile_names()
        assert names == sorted(names)

    def test_known_profiles_exist(self):
        names = get_builtin_profile_names()
        assert "nasa" in names
        assert "abomination" in names
        assert "hacker" in names
        assert "macbook" in names
        assert "server" in names
        assert "retro" in names
        assert "gamer" in names
        assert "minimal" in names
        assert "templeos" in names
        assert "haiku" in names

    def test_abomination_is_absurd(self):
        profiles = get_builtin_profiles()
        abom = profiles["abomination"]
        assert abom["os"] == "Windows 11 Pro"
        assert abom["kernel"] == "6.18.7-arch1-1"
        assert abom["cpu"] == "Apple M7 Ultra"
        assert abom["gpu"] == "NVIDIA RTX 9090 Ti"
        assert abom["memory"] == "69 PiB"
        assert abom["shell"] == "HolyC"

    def test_nasa_has_classified_gpu(self):
        profiles = get_builtin_profiles()
        assert profiles["nasa"]["gpu"] == "Classified"
        assert profiles["nasa"]["memory"] == "69 PiB"

    def test_retro_has_old_school_fields(self):
        profiles = get_builtin_profiles()
        retro = profiles["retro"]
        assert "Pentium" in retro["cpu"]
        assert "Voodoo" in retro["gpu"]
        assert retro["shell"] == "COMMAND.COM"

    def test_user_config_overrides_builtin(self, tmp_path):
        from larpfetch.cli import _get_all_profiles

        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[profiles.nasa]
os = "My Custom NASA"
cpu = "Custom CPU"
""")
        config = {
            "default": {},
            "profiles": {"nasa": {"os": "My Custom NASA", "cpu": "Custom CPU"}},
            "appearance": {},
        }
        profiles = _get_all_profiles(config)
        # User profile should override built-in nasa
        assert profiles["nasa"]["os"] == "My Custom NASA"
        assert profiles["nasa"]["cpu"] == "Custom CPU"
        # Other built-in profiles should still exist
        assert "abomination" in profiles

    def test_builtin_profiles_available_without_config(self, monkeypatch):
        from pathlib import Path

        from larpfetch.cli import _get_all_profiles

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        from larpfetch.config import load_config

        config = load_config()
        profiles = _get_all_profiles(config)
        assert len(profiles) >= 10  # at least the built-in ones
        assert "nasa" in profiles
        assert "abomination" in profiles
