"""Tests for the models module."""

from collections import OrderedDict

from larpfetch.models import (
    DENSITY_PRESETS,
    FIELD_ALIASES,
    FIELD_LABELS,
    KNOWN_FIELDS,
    DisplayConfig,
    SystemInfo,
)


class TestSystemInfo:
    def test_get_set(self):
        info = SystemInfo(fields=OrderedDict())
        info.set("os", "Linux")
        assert info.get("os") == "Linux"
        assert info.get("nonexistent", "default") == "default"

    def test_to_dict(self):
        info = SystemInfo(fields=OrderedDict([("os", "Linux"), ("cpu", "Intel")]))
        d = info.to_dict()
        assert d["os"] == "Linux"
        assert d["cpu"] == "Intel"

    def test_from_dict(self):
        info = SystemInfo.from_dict({"os": "Linux", "cpu": "Intel"})
        assert info.get("os") == "Linux"
        assert info.get("cpu") == "Intel"

    def test_from_dict_coerces_to_string(self):
        info = SystemInfo.from_dict({"count": 42, "flag": True})
        assert info.get("count") == "42"
        assert info.get("flag") == "True"

    def test_update_from(self):
        info = SystemInfo(fields=OrderedDict([("os", "Linux")]))
        info.update_from({"os": "Windows", "kernel": "5.15.0"})
        assert info.get("os") == "Windows"
        assert info.get("kernel") == "5.15.0"

    def test_update_from_empty_value_not_applied(self):
        info = SystemInfo(fields=OrderedDict([("os", "Linux")]))
        info.update_from({"os": ""})
        assert info.get("os") == "Linux"

    def test_display_items_known_fields_order(self):
        info = SystemInfo(
            fields=OrderedDict(
                [
                    ("memory", "16 GiB"),
                    ("os", "Linux"),
                    ("cpu", "Intel"),
                ]
            )
        )
        items = info.display_items()
        labels = [label for label, _ in items]
        assert "OS" in labels
        assert "CPU" in labels
        assert "Memory" in labels
        # OS should come before CPU, which comes before Memory
        os_idx = labels.index("OS")
        cpu_idx = labels.index("CPU")
        mem_idx = labels.index("Memory")
        assert os_idx < cpu_idx < mem_idx

    def test_display_items_custom_fields_after_known(self):
        info = SystemInfo(
            fields=OrderedDict(
                [
                    ("custom_field", "value"),
                    ("os", "Linux"),
                ]
            )
        )
        items = info.display_items()
        labels = [label for label, _ in items]
        os_idx = labels.index("OS")
        custom_idx = labels.index("Custom Field")
        assert os_idx < custom_idx

    def test_display_items_custom_field_label(self):
        info = SystemInfo(fields=OrderedDict([("my_custom_field", "value")]))
        items = info.display_items()
        assert items[0][0] == "My Custom Field"

    def test_known_fields_constant(self):
        assert "username" in KNOWN_FIELDS
        assert "os" in KNOWN_FIELDS
        assert "kernel" in KNOWN_FIELDS
        assert "cpu" in KNOWN_FIELDS
        assert "gpu" in KNOWN_FIELDS
        assert "memory" in KNOWN_FIELDS

    def test_field_labels_mapping(self):
        assert FIELD_LABELS["os"] == "OS"
        assert FIELD_LABELS["cpu"] == "CPU"
        assert FIELD_LABELS["gpu"] == "GPU"
        assert FIELD_LABELS["username"] == "User"
        assert FIELD_LABELS["hostname"] == "Host"

    def test_disk_detail_in_known_fields(self):
        assert "disk_detail" in KNOWN_FIELDS

    def test_disk_detail_label(self):
        assert FIELD_LABELS["disk_detail"] == "Disk Detail"

    def test_display_config_filters_fields(self):
        info = SystemInfo(
            fields=OrderedDict(
                [("os", "Linux"), ("kernel", "6.8.0"), ("cpu", "Intel")]
            )
        )
        cfg = DisplayConfig(fields=["os", "cpu"])
        items = info.display_items(cfg)
        labels = [lab for lab, _ in items]
        assert "OS" in labels
        assert "CPU" in labels
        assert "Kernel" not in labels

    def test_display_config_ordering(self):
        info = SystemInfo(
            fields=OrderedDict(
                [("os", "Linux"), ("kernel", "6.8.0"), ("cpu", "Intel")]
            )
        )
        cfg = DisplayConfig(fields=["cpu", "os"])
        items = info.display_items(cfg)
        labels = [lab for lab, _ in items]
        assert labels.index("CPU") < labels.index("OS")

    def test_display_config_custom_labels(self):
        info = SystemInfo(fields=OrderedDict([("memory", "16 GiB")]))
        cfg = DisplayConfig(field_labels={"memory": "RAM"})
        items = info.display_items(cfg)
        assert items[0][0] == "RAM"

    def test_display_config_hide_unavailable(self):
        info = SystemInfo(
            fields=OrderedDict([("os", "Linux"), ("gpu", ""), ("cpu", "Intel")])
        )
        cfg = DisplayConfig(fields=["os", "gpu", "cpu"], hide_unavailable=True)
        items = info.display_items(cfg)
        labels = [lab for lab, _ in items]
        assert "GPU" not in labels
        assert "OS" in labels
        assert "CPU" in labels

    def test_display_config_show_unavailable_by_default(self):
        info = SystemInfo(
            fields=OrderedDict([("os", "Linux"), ("gpu", "")])
        )
        cfg = DisplayConfig(fields=["os", "gpu"])
        items = info.display_items(cfg)
        labels = [lab for lab, _ in items]
        assert "GPU" in labels

    def test_display_config_field_aliases(self):
        info = SystemInfo(
            fields=OrderedDict([("hostname", "myhost"), ("memory", "16 GiB")])
        )
        cfg = DisplayConfig(fields=["host", "ram"])
        items = info.display_items(cfg)
        labels = [lab for lab, _ in items]
        assert "Host" in labels
        assert "Memory" in labels


class TestDensityPresets:
    def test_minimal_has_core_fields(self):
        fields = DENSITY_PRESETS["minimal"]
        assert "os" in fields
        assert "kernel" in fields
        assert "cpu" in fields
        assert "memory" in fields

    def test_compact_has_more_fields(self):
        assert len(DENSITY_PRESETS["compact"]) > len(DENSITY_PRESETS["minimal"])

    def test_all_presets_exist(self):
        assert "minimal" in DENSITY_PRESETS
        assert "compact" in DENSITY_PRESETS


class TestFieldAliases:
    def test_host_alias(self):
        assert FIELD_ALIASES["host"] == "hostname"

    def test_packages_alias(self):
        assert FIELD_ALIASES["packages"] == "package_manager"

    def test_ram_alias(self):
        assert FIELD_ALIASES["ram"] == "memory"


class TestDisplayEntries:
    def test_returns_key_label_value(self):
        info = SystemInfo(fields=OrderedDict([("os", "Linux"), ("cpu", "Intel")]))
        entries = info.display_entries()
        keys = [k for k, _, _ in entries]
        assert "os" in keys
        assert "cpu" in keys
        for key, label, value in entries:
            if key == "os":
                assert label == "OS"
                assert value == "Linux"

    def test_respects_field_filter(self):
        info = SystemInfo(
            fields=OrderedDict([("os", "Linux"), ("cpu", "Intel"), ("kernel", "6.8")])
        )
        entries = info.display_entries(DisplayConfig(fields=["os", "cpu"]))
        keys = [k for k, _, _ in entries]
        assert keys == ["os", "cpu"]

    def test_alias_maps_to_real_key(self):
        info = SystemInfo(fields=OrderedDict([("hostname", "box")]))
        entries = info.display_entries(DisplayConfig(fields=["host"]))
        assert entries[0][0] == "hostname"

    def test_display_items_consistent_with_entries(self):
        info = SystemInfo(fields=OrderedDict([("os", "Linux"), ("cpu", "Intel")]))
        items = info.display_items()
        entries = info.display_entries()
        assert items == [(label, value) for _, label, value in entries]
