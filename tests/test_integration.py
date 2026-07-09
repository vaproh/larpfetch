"""Integration tests for larpfetch CLI behavior."""

from pathlib import Path

import pytest

from larpfetch.cli import main


@pytest.fixture
def no_config(monkeypatch):
    monkeypatch.setattr(
        "larpfetch.config.DEFAULT_CONFIG_PATH",
        Path("/nonexistent/config.toml"),
    )


@pytest.fixture
def sample_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[default]
os = "Arch Linux"
distro = "Arch Linux"
hostname = "btw-i-use-arch"
kernel = "6.99.0-larp"
cpu = "AMD Ryzen 9 9950X3D"
gpu = "NVIDIA RTX 5090"
memory = "128 GiB"
shell = "zsh"

[profiles.nasa]
os = "NASA Linux"
hostname = "mainframe-01"
cpu = "Quantum Potato 9000"
gpu = "Classified"
memory = "69 PiB"

[profiles.abomination]
os = "Windows 11 Pro"
kernel = "6.18.7-arch1-1"
cpu = "Apple M7 Ultra"
gpu = "NVIDIA RTX 9090 Ti"
shell = "HolyC"
de = "GNOME 83"
package_manager = "apt btw"

[appearance]
color = false
show_authenticity = true
easter_eggs = true
""")
    return config_file


class TestIntegrationNoConfig:
    def test_runs_without_config(self, capsys, no_config):
        main([])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_profile_not_found(self, no_config):
        with pytest.raises(SystemExit) as exc_info:
            main(["--profile", "nonexistent"])
        assert exc_info.value.code == 1

    def test_cli_override_appears_in_output(self, capsys, no_config):
        main(["--set", "os=Fedora btw"])
        captured = capsys.readouterr()
        assert "Fedora btw" in captured.out


class TestIntegrationWithConfig:
    def test_default_profile_applied(self, capsys, sample_config):
        main(["--config", str(sample_config)])
        captured = capsys.readouterr()
        assert "Arch Linux" in captured.out

    def test_custom_profile_selected(self, capsys, sample_config):
        main(["--config", str(sample_config), "-p", "nasa"])
        captured = capsys.readouterr()
        assert "NASA Linux" in captured.out
        assert "Quantum Potato 9000" in captured.out

    def test_profile_inheritance(self, capsys, sample_config):
        # nasa profile doesn't set shell, should inherit from default (zsh)
        main(["--config", str(sample_config), "-p", "nasa"])
        captured = capsys.readouterr()
        assert "zsh" in captured.out

    def test_abomination_profile(self, capsys, sample_config):
        main(["--config", str(sample_config), "-p", "abomination"])
        captured = capsys.readouterr()
        assert "Windows 11 Pro" in captured.out
        assert "Apple M7 Ultra" in captured.out
        assert "HolyC" in captured.out
        assert "GNOME 83" in captured.out

    def test_cli_overrides_profile(self, capsys, sample_config):
        main([
            "--config", str(sample_config),
            "-p", "nasa",
            "--set", "os=Hacked Linux",
        ])
        captured = capsys.readouterr()
        assert "Hacked Linux" in captured.out
        assert "NASA Linux" not in captured.out

    def test_real_shit_ignores_default_profile(self, capsys, sample_config):
        main(["--config", str(sample_config), "--real-shit"])
        captured = capsys.readouterr()
        # Check that default-profile-only values are absent
        # (hostname and kernel are fake in the config; real values differ)
        assert "btw-i-use-arch" not in captured.out
        assert "6.99.0-larp" not in captured.out
        assert "AMD Ryzen 9 9950X3D" not in captured.out

    def test_real_shit_ignores_selected_profile(self, capsys, sample_config):
        main(["--config", str(sample_config), "-p", "nasa", "--real-shit"])
        captured = capsys.readouterr()
        assert "NASA Linux" not in captured.out
        assert "Quantum Potato 9000" not in captured.out

    def test_real_shit_ignores_cli_overrides(self, capsys, sample_config):
        main([
            "--config", str(sample_config),
            "--real-shit",
            "--set", "os=Fake OS",
        ])
        captured = capsys.readouterr()
        assert "Fake OS" not in captured.out


class TestIntegrationAppearance:
    def test_authenticity_shown(self, capsys, sample_config):
        main(["--config", str(sample_config)])
        captured = capsys.readouterr()
        assert "Authenticity" in captured.out

    def test_authenticity_100_for_real_shit(self, capsys, sample_config):
        main(["--config", str(sample_config), "--real-shit"])
        captured = capsys.readouterr()
        assert "100%" in captured.out


class TestIntegrationEdgeCases:
    def test_repeated_set(self, capsys, no_config):
        main([
            "--set", "os=Windows",
            "--set", "kernel=Arch",
            "--set", "cpu=Apple M7",
        ])
        captured = capsys.readouterr()
        assert "Windows" in captured.out
        assert "Arch" in captured.out
        assert "Apple M7" in captured.out

    def test_empty_value_override(self, capsys, no_config):
        # Setting to empty should not override real values
        main(["--set", "os="])
        captured = capsys.readouterr()
        # Real OS should still be shown
        assert len(captured.out) > 0
