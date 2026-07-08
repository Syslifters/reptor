"""
Unit tests for the --json output flag on `reptor plugins`.

Mirrors the test style of the existing PluginMeta tests; runs without a live
SysReptor server (no integration marker).
"""

import io
import json

from reptor.lib.plugins.PluginMeta import PluginMeta
from reptor.plugins.core.Plugins.Plugins import Plugins


def _make_plugin(name, *, category="core", summary="", tags=None,
                 author="", version="", license="", website=""):
    meta = {
        "summary": summary,
        "tags": list(tags or []),
        "author": author,
        "version": version,
        "license": license,
        "website": website,
    }
    plugin = PluginMeta(meta)
    plugin.name = name
    plugin.category = category
    return plugin


class TestPluginsJsonFlag:
    def _run_list(self, plugins, json_flag):
        """Construct a Plugins instance and capture stdout from _list()."""
        instance = Plugins(json=json_flag)
        # Replace Base.print with a captured stdout writer
        buf = io.StringIO()
        instance.print = lambda *a, **kw: print(*a, file=buf, **kw)
        instance._list(plugins)
        return buf.getvalue()

    def test_plugin_to_dict_full_fields(self):
        plugin = _make_plugin(
            "MyTool",
            category="tools",
            summary="Parses X reports",
            tags=["scanner", "web"],
            author="Alice",
            version="1.2.3",
            license="MIT",
            website="https://example.com",
        )
        result = Plugins(json=True)._plugin_to_dict(plugin)
        assert result == {
            "name": "MyTool",
            "summary": "Parses X reports",
            "tags": ["scanner", "web"],
            "category": "tools",
            "author": "Alice",
            "version": "1.2.3",
            "license": "MIT",
            "website": "https://example.com",
        }

    def test_plugin_to_dict_omits_overwrites_when_none(self):
        plugin = _make_plugin("Plain", summary="", tags=[])
        result = Plugins(json=True)._plugin_to_dict(plugin)
        assert "overwrites" not in result

    def test_plugin_to_dict_includes_overwrites_when_present(self):
        base = _make_plugin("Base", category="tools")
        override = _make_plugin("Mine", category="private")
        override.set_overwrites_plugin(base)
        result = Plugins(json=True)._plugin_to_dict(override)
        assert result["overwrites"] == {"name": "Base", "category": "tools"}

    def test_plugin_to_dict_sorts_tags_when_set(self):
        plugin = _make_plugin("Tagged", tags=["b", "a"])
        plugin.tags = {"b", "a"}
        result = Plugins(json=True)._plugin_to_dict(plugin)
        assert result["tags"] == ["a", "b"]

    def test_plugin_to_dict_handles_none_tags(self):
        plugin = _make_plugin("NoTags", tags=[])
        plugin.tags = None
        result = Plugins(json=True)._plugin_to_dict(plugin)
        assert result["tags"] == []

    def test_list_outputs_valid_json_array(self):
        plugins = [
            _make_plugin("A", summary="alpha", tags=["x"]),
            _make_plugin("B", summary="beta", tags=[]),
        ]
        output = self._run_list(plugins, json_flag=True)
        parsed = json.loads(output)
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert [p["name"] for p in parsed] == ["A", "B"]
        assert parsed[0]["summary"] == "alpha"
        assert parsed[0]["tags"] == ["x"]

    def test_list_with_no_plugins_returns_empty_json_array(self):
        output = self._run_list([], json_flag=True)
        assert json.loads(output) == []

    def test_search_skips_searching_for_banner_when_json(self, monkeypatch):
        """--json should suppress the colored "Searching for: X" banner."""
        import reptor.subcommands as subcommands

        groups = {"core": ("Core", [_make_plugin("Apple", tags=["fruit"]), _make_plugin("Avocado", tags=["fruit"])])}
        monkeypatch.setattr(subcommands, "SUBCOMMANDS_GROUPS", groups)

        instance = Plugins(json=True, search="A")
        # Replace the console.print with a sentinel that raises if called
        from reptor.lib.console import reptor_console

        called = {"count": 0}

        def fake_print(*args, **kwargs):
            called["count"] += 1

        monkeypatch.setattr(reptor_console, "print", fake_print)
        # _search walks subcommands.SUBCOMMANDS_GROUPS and calls console.print
        # only when self.search is truthy and self.json is False.
        instance._search()
        assert called["count"] == 0

    def test_search_shows_banner_when_not_json(self, monkeypatch):
        """Without --json, the colored banner is preserved."""
        import reptor.subcommands as subcommands

        groups = {"core": ("Core", [_make_plugin("Apple", tags=["fruit"]), _make_plugin("Avocado", tags=["fruit"])])}
        monkeypatch.setattr(subcommands, "SUBCOMMANDS_GROUPS", groups)

        instance = Plugins(json=False, search="A")
        from reptor.lib.console import reptor_console

        called = {"count": 0}

        def fake_print(*args, **kwargs):
            called["count"] += 1

        monkeypatch.setattr(reptor_console, "print", fake_print)
        instance._search()
        assert called["count"] >= 1  # Banner printed at least once

    def test_add_arguments_registers_json_flag(self, monkeypatch):
        """--json must be a registered CLI flag on the plugin parser."""
        import argparse

        parser = argparse.ArgumentParser(prog="reptor")
        Plugins.add_arguments(parser, plugin_filepath=None)
        # Parse with --json; expect json=True
        args = parser.parse_args(["--json"])
        assert getattr(args, "json", False) is True

        # Without --json; expect json=False
        args = parser.parse_args([])
        assert getattr(args, "json", False) is False
