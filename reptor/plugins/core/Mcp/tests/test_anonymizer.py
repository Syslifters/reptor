import re
from reptor.plugins.core.Mcp.Anonymizer import Anonymizer


class TestAnonymizer:
    def test_anonymize_produces_redacted_format(self):
        """Verify output matches REDACTED_<8-char-hex> pattern."""
        anonymizer = Anonymizer()

        project_id = "proj-123"
        finding = {
            "title": "SQL Injection",
            "affected_components": ["192.168.1.5", "example.com"]
        }

        anonymized = anonymizer.anonymize(project_id, finding)

        # All components should match REDACTED_<8 hex chars> pattern
        for component in anonymized["affected_components"]:
            assert re.match(r"^REDACTED_[a-f0-9]{8}$", component), \
                f"Component '{component}' doesn't match expected format"

    def test_anonymize_consistency(self):
        """Same input should always produce same output."""
        anonymizer = Anonymizer()

        project_id = "proj-123"
        finding = {
            "title": "SQL Injection",
            "affected_components": ["192.168.1.5", "192.168.1.6"]
        }

        # First pass
        anonymized_1 = anonymizer.anonymize(project_id, finding)

        # Second pass with same input
        anonymized_2 = anonymizer.anonymize(project_id, finding)

        # Should produce identical results
        assert anonymized_1["affected_components"] == anonymized_2["affected_components"]

    def test_deanonymize_restores_originals(self):
        """Deanonymization should restore original values."""
        anonymizer = Anonymizer()
        project_id = "proj-123"
        original_finding = {
            "affected_components": ["192.168.1.5"]
        }

        # Anonymize first to populate map
        anonymized = anonymizer.anonymize(project_id, original_finding)
        mock_value = anonymized["affected_components"][0]

        # Simulate LLM returning the mocked data
        finding_from_llm = {
            "title": "New Title",
            "affected_components": [mock_value]
        }

        restored = anonymizer.deanonymize(project_id, finding_from_llm)
        assert restored["affected_components"] == ["192.168.1.5"]

    def test_deanonymize_handles_unknowns(self):
        """Unknown components should pass through unchanged."""
        anonymizer = Anonymizer()
        project_id = "proj-123"

        finding_from_llm = {
            "affected_components": ["NEW_COMPONENT_X"]
        }

        restored = anonymizer.deanonymize(project_id, finding_from_llm)
        assert restored["affected_components"] == ["NEW_COMPONENT_X"]

    def test_deanonymize_mixed(self):
        """Mix of known mocks and new components."""
        anonymizer = Anonymizer()
        project_id = "proj-123"

        original = {"affected_components": ["1.1.1.1"]}
        anonymized = anonymizer.anonymize(project_id, original)
        mock_ip = anonymized["affected_components"][0]

        # LLM returns one known mock and one new component
        finding_from_llm = {
            "affected_components": [mock_ip, "2.2.2.2"]
        }

        restored = anonymizer.deanonymize(project_id, finding_from_llm)
        assert restored["affected_components"] == ["1.1.1.1", "2.2.2.2"]

    def test_project_isolation(self):
        """Same component in different projects should get different mocks."""
        anonymizer = Anonymizer()

        project_a = "proj-A"
        project_b = "proj-B"
        comp = "192.168.1.1"

        anon_a = anonymizer.anonymize(project_a, {"affected_components": [comp]})
        anon_b = anonymizer.anonymize(project_b, {"affected_components": [comp]})

        # They should have different mocks because hash includes project_id
        assert anon_a["affected_components"][0] != anon_b["affected_components"][0]

        # But deanonymization should still work correctly for each project
        restored_a = anonymizer.deanonymize(project_a, anon_a)
        assert restored_a["affected_components"][0] == comp

        restored_b = anonymizer.deanonymize(project_b, anon_b)
        assert restored_b["affected_components"][0] == comp

    def test_handles_complex_components(self):
        """Should handle complex component strings without issues."""
        anonymizer = Anonymizer()
        project_id = "proj-123"

        complex_components = [
            "192.168.1.5 (OS: Windows Server 2019, HOSTNAME: DC01)",
            "https://example.com/api/v1/users",
            "10.0.0.1:8080",
            "my-internal-server.local",
        ]

        finding = {"affected_components": complex_components}
        anonymized = anonymizer.anonymize(project_id, finding)

        # All should be anonymized
        for component in anonymized["affected_components"]:
            assert re.match(r"^REDACTED_[a-f0-9]{8}$", component)

        # All should be restorable
        restored = anonymizer.deanonymize(project_id, anonymized)
        assert restored["affected_components"] == complex_components

    def test_empty_components(self):
        """Empty or missing affected_components should be handled gracefully."""
        anonymizer = Anonymizer()
        project_id = "proj-123"

        # Empty list
        finding_empty = {"affected_components": []}
        assert anonymizer.anonymize(project_id, finding_empty) == finding_empty

        # Missing key
        finding_no_key = {"title": "Test"}
        assert anonymizer.anonymize(project_id, finding_no_key) == finding_no_key
