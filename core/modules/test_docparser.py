import json
import unittest

from core.modules.docparser import DocParser


class TestModelsParsing(unittest.TestCase):
    example_docs = """
    Author: Willy Wonka
    Version: 1.5
    Website: https://github.com/Syslifters/reptor
    License: MIT
    Tags: owasp, zap

    Short Help:
    Parses OWASPZap XML and JSON reports

    Description:
    Parses OWASPZap generated reports in either XML or JSON

    Make sure you verify what type of findings you export.

    Recommended settings are to only export Medium and higher findings
    """

    def test_perfect_docs(self):
        module_docs = DocParser.parse(self.example_docs)

        self.assertTrue(module_docs.author, "Willy Wonka")
        self.assertTrue(module_docs.version, "1.5")
        self.assertTrue(module_docs.website, "https://github.com/Syslifters/reptor")
        self.assertTrue(module_docs.license, "MIT")
        self.assertTrue(module_docs.short_help, "Parses OWASPZap XML and JSON reports")

        self.assertTrue(
            module_docs.description,
            """Parses OWASPZap generated reports in either XML or JSON\n\nMake sure you verify what type of findings you export.\n\nRecommended settings are to only export Medium and higher findings""",
        )


if __name__ == "__main__":
    unittest.main()
