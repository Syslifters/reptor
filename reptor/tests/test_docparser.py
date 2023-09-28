from reptor.lib.plugins.PluginMeta import PluginMeta


class TestPluginMeta:
    example_docs = {
        "author": "Willy Wonka",
        "version": "1.5",
        "website": "https://github.com/Syslifters/reptor",
        "license": "MIT",
        "summary": "Parses OWASPZap XML and JSON reports",
    }

    def test_perfect_docs(self):
        plugin_meta = PluginMeta(self.example_docs)

        assert plugin_meta.author == "Willy Wonka"
        assert plugin_meta.version == "1.5"
        assert plugin_meta.website == "https://github.com/Syslifters/reptor"
        assert plugin_meta.license == "MIT"
        assert plugin_meta.summary == "Parses OWASPZap XML and JSON reports"
