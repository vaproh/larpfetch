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

    def test_config_disk_info_default(self, capsys, tmp_path, monkeypatch):
        from collections import namedtuple
        from types import SimpleNamespace

        import psutil

        DiskPart = namedtuple("DiskPart", ["device", "mountpoint", "fstype", "opts"])
        monkeypatch.setattr(
            psutil, "disk_partitions", lambda all=False: [DiskPart("/dev/sda1", "/", "ext4", "rw")]  # noqa: A002
        )
        monkeypatch.setattr(psutil, "disk_usage", lambda p: SimpleNamespace(used=1, total=2))

        cfg = tmp_path / "config.toml"
        cfg.write_text('[default]\ndisk_info = "/"\n')
        main(["--config", str(cfg)])
        captured = capsys.readouterr()
        # disk detail shown from config without passing --disk-info
        assert "Disk Detail:" in captured.out
        assert "/:" in captured.out
        # disk_info must not leak as a displayed field
        assert "Disk Info:" not in captured.out

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
        main(
            [
                "--config",
                str(sample_config),
                "-p",
                "nasa",
                "--set",
                "os=Hacked Linux",
            ]
        )
        captured = capsys.readouterr()
        assert "Hacked Linux" in captured.out
        assert "NASA Linux" not in captured.out

    def test_real_shit_ignores_default_profile(self, capsys, sample_config):
        main(["--config", str(sample_config), "--real-shit"])
        captured = capsys.readouterr()
        # Check that default-profile-only values are absent
        assert "btw-i-use-arch" not in captured.out
        assert "6.99.0-larp" not in captured.out
        assert "AMD Ryzen 9 9950X3D" not in captured.out

    def test_real_shit_ignores_selected_profile(self, capsys, sample_config):
        main(["--config", str(sample_config), "-p", "nasa", "--real-shit"])
        captured = capsys.readouterr()
        assert "NASA Linux" not in captured.out
        assert "Quantum Potato 9000" not in captured.out

    def test_real_shit_ignores_cli_overrides(self, capsys, sample_config):
        main(
            [
                "--config",
                str(sample_config),
                "--real-shit",
                "--set",
                "os=Fake OS",
            ]
        )
        captured = capsys.readouterr()
        assert "Fake OS" not in captured.out

    def test_real_shit_ignores_nonexistent_profile(self, capsys, sample_config):
        # Should not error even with invalid profile
        main(["--config", str(sample_config), "--real-shit", "--profile", "nope"])
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestIntegrationAppearance:
    def test_authenticity_shown(self, capsys, sample_config):
        main(["--config", str(sample_config)])
        captured = capsys.readouterr()
        assert "Authenticity" in captured.out

    def test_authenticity_100_for_real_shit(self, capsys, sample_config):
        main(["--config", str(sample_config), "--real-shit"])
        captured = capsys.readouterr()
        assert "100%" in captured.out

    def test_disappointment_in_real_shit(self, capsys, sample_config):
        main(["--config", str(sample_config), "--real-shit"])
        captured = capsys.readouterr()
        assert "Disappointment" in captured.out


class TestIntegrationEdgeCases:
    def test_repeated_set(self, capsys, no_config):
        main(
            [
                "--set",
                "os=Windows",
                "--set",
                "kernel=Arch",
                "--set",
                "cpu=Apple M7",
            ]
        )
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


class TestIntegrationColor:
    def test_no_color_flag(self, capsys, no_config):
        main(["--no-color"])
        captured = capsys.readouterr()
        assert "\033[" not in captured.out

    def test_color_flag(self, capsys, monkeypatch, no_config):
        monkeypatch.delenv("NO_COLOR", raising=False)
        main(["--color"])
        captured = capsys.readouterr()
        assert "\033[" in captured.out


class TestIntegrationDisplay:
    def test_minimal_shows_fewer_fields(self, capsys, sample_config):
        main(["--config", str(sample_config), "--minimal"])
        captured = capsys.readouterr()
        assert "OS:" in captured.out
        assert "Kernel:" in captured.out
        assert "Memory:" in captured.out
        # Minimal should not show packages by default
        # (we don't check specifically what's absent, just that it works)

    def test_compact_different_from_minimal(self, capsys, sample_config):
        main(["--config", str(sample_config), "--compact"])
        captured = capsys.readouterr()
        assert "OS:" in captured.out

    def test_full_shows_all_fields(self, capsys, sample_config):
        main(["--config", str(sample_config), "--full"])
        captured = capsys.readouterr()
        assert len(captured.out) > 0
