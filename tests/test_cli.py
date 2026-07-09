"""Tests for the CLI module."""

import pytest

from larpfetch.cli import build_parser, main


class TestBuildParser:
    def test_default_args(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.profile is None
        assert args.real_shit is False
        assert args.list_profiles is False
        assert args.show_config is False
        assert args.config is None
        assert args.set == []

    def test_profile_short(self):
        parser = build_parser()
        args = parser.parse_args(["-p", "nasa"])
        assert args.profile == "nasa"

    def test_profile_long(self):
        parser = build_parser()
        args = parser.parse_args(["--profile", "nasa"])
        assert args.profile == "nasa"

    def test_real_shit(self):
        parser = build_parser()
        args = parser.parse_args(["--real-shit"])
        assert args.real_shit is True

    def test_list_profiles(self):
        parser = build_parser()
        args = parser.parse_args(["--list-profiles"])
        assert args.list_profiles is True

    def test_show_config(self):
        parser = build_parser()
        args = parser.parse_args(["--show-config"])
        assert args.show_config is True

    def test_config_path(self):
        parser = build_parser()
        args = parser.parse_args(["--config", "/path/to/config.toml"])
        assert args.config == "/path/to/config.toml"

    def test_single_set(self):
        parser = build_parser()
        args = parser.parse_args(["--set", "cpu=Quantum Potato 9000"])
        assert args.set == ["cpu=Quantum Potato 9000"]

    def test_repeated_set(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "--set",
                "os=Windows 11 Pro",
                "--set",
                "kernel=6.18.7-arch1-1",
            ]
        )
        assert args.set == ["os=Windows 11 Pro", "kernel=6.18.7-arch1-1"]

    def test_combined_args(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "-p",
                "nasa",
                "--set",
                "cpu=Fast",
                "--real-shit",
            ]
        )
        assert args.profile == "nasa"
        assert args.set == ["cpu=Fast"]
        assert args.real_shit is True

    def test_color_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--color"])
        assert args.color is True

    def test_no_color_flag(self):
        parser = build_parser()
        args = parser.parse_args(["--no-color"])
        assert args.no_color is True


class TestMain:
    def test_help_exits_cleanly(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "larpfetch" in captured.out.lower() or "larpfetch" in captured.out

    def test_version_exits_cleanly(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "0.1.0" in captured.out

    def test_list_profiles_no_config(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--list-profiles"])
        captured = capsys.readouterr()
        # Built-in profiles should be listed even without config
        assert "nasa" in captured.out
        assert "abomination" in captured.out

    def test_list_profiles_with_config(self, capsys, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[profiles.nasa]
os = "NASA Linux"

[profiles.test]
os = "Test OS"
""")
        main(["--config", str(config_file), "--list-profiles"])
        captured = capsys.readouterr()
        assert "nasa" in captured.out
        assert "test" in captured.out

    def test_list_profiles_empty_os_fallback(self, capsys, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[profiles.custom]
my_field = "value"
""")
        main(["--config", str(config_file), "--list-profiles"])
        captured = capsys.readouterr()
        assert "custom" in captured.out
        assert "Custom identity" in captured.out

    def test_show_config_no_config(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--show-config"])
        captured = capsys.readouterr()
        assert "Default profile:" in captured.out

    def test_show_config_with_config(self, capsys, tmp_path):
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[default]
os = "Arch Linux"

[appearance]
color = true
show_authenticity = true
""")
        main(["--config", str(config_file), "--show-config"])
        captured = capsys.readouterr()
        assert "os = Arch Linux" in captured.out
        assert "color = true" in captured.out
        assert "show_authenticity = true" in captured.out

    def test_missing_profile_exits_with_error(self, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        with pytest.raises(SystemExit) as exc_info:
            main(["--profile", "nonexistent"])
        assert exc_info.value.code == 1

    def test_default_run_produces_output(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main([])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_real_shit_produces_output(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--real-shit"])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_real_shit_ignores_nonexistent_profile(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        # Should not error even though profile doesn't exist
        main(["--real-shit", "--profile", "nonexistent"])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_cli_override_in_output(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--set", "os=Arch Linux btw"])
        captured = capsys.readouterr()
        assert "Arch Linux btw" in captured.out

    def test_multiple_cli_overrides(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(
            [
                "--set",
                "os=Windows 11 Pro",
                "--set",
                "kernel=6.18.7-arch1-1",
            ]
        )
        captured = capsys.readouterr()
        assert "Windows 11 Pro" in captured.out
        assert "6.18.7-arch1-1" in captured.out

    def test_set_empty_key_exits_with_error(self, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        with pytest.raises(SystemExit) as exc_info:
            main(["--set", "=value"])
        assert exc_info.value.code == 1

    def test_set_no_equals_exits_with_error(self, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        with pytest.raises(SystemExit) as exc_info:
            main(["--set", "novalue"])
        assert exc_info.value.code == 1

    def test_impossible_combination_accepted(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(
            [
                "--set",
                "os=Windows 11 Pro",
                "--set",
                "kernel=6.18.7-arch1-1",
                "--set",
                "cpu=Apple M7 Ultra",
                "--set",
                "gpu=NVIDIA RTX 9090 Ti",
                "--set",
                "memory=69 PiB",
                "--set",
                "shell=HolyC",
            ]
        )
        captured = capsys.readouterr()
        assert "Windows 11 Pro" in captured.out
        assert "Apple M7 Ultra" in captured.out
        assert "HolyC" in captured.out

    def test_config_not_found_exits_with_error(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--config", "/nonexistent/config.toml"])
        assert exc_info.value.code == 1

    def test_custom_field_via_cli(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--set", "my_custom_field=custom_value"])
        captured = capsys.readouterr()
        assert "custom_value" in captured.out

    def test_no_color_flag(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        main(["--no-color"])
        captured = capsys.readouterr()
        assert "\033[" not in captured.out

    def test_color_flag_forced(self, capsys, monkeypatch):
        from pathlib import Path

        monkeypatch.setattr(
            "larpfetch.config.DEFAULT_CONFIG_PATH",
            Path("/nonexistent/config.toml"),
        )
        monkeypatch.delenv("NO_COLOR", raising=False)
        # Even in non-tty, --color should add ANSI codes
        main(["--color"])
        captured = capsys.readouterr()
        assert "\033[" in captured.out
