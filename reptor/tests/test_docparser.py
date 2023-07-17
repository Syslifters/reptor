import unittest

from reptor.lib.plugins.DocParser import DocParser


class TestModelsParsing(unittest.TestCase):
    example_docs = {
        "author": "Willy Wonka",
        "version": "1.5",
        "website": "https://github.com/Syslifters/reptor",
        "license": "MIT",
        "summary": "Parses OWASPZap XML and JSON reports",
    }

    def test_perfect_docs(self):
        module_docs = DocParser.parse(self.example_docs)

        self.assertTrue(module_docs.author, "Willy Wonka")
        self.assertTrue(module_docs.version, "1.5")
        self.assertTrue(module_docs.website, "https://github.com/Syslifters/reptor")
        self.assertTrue(module_docs.license, "MIT")
        self.assertTrue(module_docs.summary, "Parses OWASPZap XML and JSON reports")


if __name__ == "__main__":
    unittest.main()
