"""Tests for the models module."""

from collections import OrderedDict

from larpfetch.models import FIELD_LABELS, KNOWN_FIELDS, SystemInfo


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
