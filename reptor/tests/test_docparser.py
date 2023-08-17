from reptor.lib.plugins.DocParser import DocParser


class TestDocParser:
    example_docs = {
        "author": "Willy Wonka",
        "version": "1.5",
        "website": "https://github.com/Syslifters/reptor",
        "license": "MIT",
        "summary": "Parses OWASPZap XML and JSON reports",
    }

    def test_perfect_docs(self):
        module_docs = DocParser.parse(self.example_docs)

        assert module_docs.author == "Willy Wonka"
        assert module_docs.version == "1.5"
        assert module_docs.website == "https://github.com/Syslifters/reptor"
        assert module_docs.license == "MIT"
        assert module_docs.summary == "Parses OWASPZap XML and JSON reports"
