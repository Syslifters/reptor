from reptor.plugins.core.Mcp.FieldExcluder import (
    FieldExcluder,
    format_remove_fields,
    parse_remove_fields,
)

class TestFieldExcluderBasic:
    """Test basic field removal functionality."""

    def test_remove_single_field(self):
        """Test removing a single field from a dictionary."""
        excluder = FieldExcluder(exclude_fields=["affected_components"])
        data = {"title": "X", "affected_components": ["1.1.1.1"]}
        result = excluder.remove_fields(data)

        assert result == {"title": "X"}
        assert "affected_components" not in result

    def test_remove_multiple_fields(self):
        """Test removing multiple fields from a dictionary."""
        excluder = FieldExcluder(
            exclude_fields=["affected_components", "internal_notes", "severities"]
        )
        data = {
            "title": "X",
            "affected_components": ["1.1.1.1"],
            "internal_notes": "Some notes",
            "severities": ["High", "Medium"],
        }
        result = excluder.remove_fields(data)

        assert result == {"title": "X"}
        assert "affected_components" not in result
        assert "internal_notes" not in result
        assert "severities" not in result

    def test_non_existent_field(self):
        """Test requesting to remove a field that doesn't exist."""
        excluder = FieldExcluder(exclude_fields=["non_existent_field"])
        data = {"title": "X", "affected_components": ["1.1.1.1"]}
        result = excluder.remove_fields(data)

        assert result == {"title": "X", "affected_components": ["1.1.1.1"]}
        assert "non_existent_field" not in result

    def test_empty_exclude_list(self):
        """Test that no fields are removed when exclude list is empty."""
        excluder = FieldExcluder(exclude_fields=[])
        data = {"title": "X", "affected_components": ["1.1.1.1"]}
        result = excluder.remove_fields(data)

        assert result == {"title": "X", "affected_components": ["1.1.1.1"]}

class TestFieldExcluderNestedFields:
    """Test removal of nested fields."""

    def test_nested_field_removal(self):
        """Test removing fields from nested data objects."""
        excluder = FieldExcluder(exclude_fields=["cvss"])
        data = {"title": "X", "data": {"cvss": 9.8, "description": "Test"}}
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {"title": "X", "data": {"description": "Test"}}
        assert "cvss" not in result["data"]
        assert result["data"]["description"] == "Test"

    def test_nested_field_removal_not_affecting_parent(self):
        """Test removing fields from nested data objects."""
        excluder = FieldExcluder(exclude_fields=["data.cvss"])
        data = {"title": "X", "cvss": 5, "data": {"cvss": 9.8, "description": "Test"}}
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {"title": "X", "cvss": 5, "data": {"description": "Test"}}
        assert "cvss" not in result["data"]
        assert result["data"]["description"] == "Test"

    def test_multiple_levels_of_nesting(self):
        """Test removing fields at multiple nesting levels."""
        excluder = FieldExcluder(exclude_fields=["security_impact"])
        data = {
            "title": "X",
            "details": {
                "security_impact": "Critical",
                "technical_details": {"risk_level": "High"},
            },
        }
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {
            "title": "X",
            "details": {
                "technical_details": {"risk_level": "High"},
            },
        }
        assert "security_impact" not in result["details"]
        assert result["details"]["technical_details"]["risk_level"] == "High"


class TestFieldExcluderArrayFields:
    """Test removal of fields from array items."""

    def test_remove_field_from_array_items(self):
        """Test removing a field from each item in an array."""
        excluder = FieldExcluder(exclude_fields=["address"])
        data = {
            "title": "X",
            "affected_components": [
                {"host": "server1", "address": "192.168.1.1"},
                {"host": "server2", "address": "192.168.1.2"},
            ],
        }
        result = excluder.remove_fields(data)

        assert result == {
            "title": "X",
            "affected_components": [
                {"host": "server1"},
                {"host": "server2"},
            ],
        }

        assert "address" not in result["affected_components"][0]
        assert "address" not in result["affected_components"][1]

    def test_remove_nested_field_from_array_items(self):
        """Test removing nested field from each item in an array."""
        excluder = FieldExcluder(exclude_fields=["data.cvss"])
        data = {
            "title": "X",
            "findings": [
                {"id": 1, "data": {"title": "Finding 1", "cvss": 9.8}},
                {"id": 2, "data": {"title": "Finding 2", "cvss": 7.5}},
            ],
        }
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {
            "title": "X",
            "findings": [
                {"id": 1, "data": {"title": "Finding 1"}},
                {"id": 2, "data": {"title": "Finding 2"}},
            ],
        }
        assert "cvss" not in result["findings"][0]["data"]
        assert "cvss" not in result["findings"][1]["data"]

    def test_remove_field_from_nested_array(self):
        """Test removing field from items in nested arrays."""
        excluder = FieldExcluder(exclude_fields=["description"])
        data = {
            "title": "X",
            "resources": [
                {
                    "id": 1,
                    "details": [
                        {"type": "server", "description": "Server details"},
                        {"type": "network", "description": "Network details"},
                    ],
                }
            ],
        }
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {
            "title": "X",
            "resources": [
                {
                    "id": 1,
                    "details": [
                        {"type": "server"},
                        {"type": "network"},
                    ],
                }
            ],
        }
        assert "description" not in result["resources"][0]["details"][0]
        assert "description" not in result["resources"][0]["details"][1]


class TestFieldExcluderValidation:
    """Test field validation and error handling."""

    def test_empty_string_field_name(self):
        """Test that empty string field names are ignored."""
        excluder = FieldExcluder(
            exclude_fields=["", "  ", "valid_field", "affected_components"]
        )
        data = {"title": "X", "affected_components": ["1.1.1.1"]}
        result = excluder.remove_fields(data)

        assert result == {"title": "X"}
        assert "affected_components" not in result


class TestFieldExcluderEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_data(self):
        """Test removing fields from empty data."""
        excluder = FieldExcluder(exclude_fields=["affected_components"])
        result = excluder.remove_fields({})

        assert result == {}

    def test_data_with_only_removed_fields(self):
        """Test removing all fields in data."""
        excluder = FieldExcluder(
            exclude_fields=["title", "affected_components", "internal_notes"]
        )
        data = {
            "title": "X",
            "affected_components": ["1.1.1.1"],
            "internal_notes": "Some notes",
        }
        result = excluder.remove_fields(data)

        assert result == {}

    def test_multiple_exclusions_with_mixed_structures(self):
        """Test removing multiple fields from complex nested structures."""
        excluder = FieldExcluder(
            exclude_fields=[
                "affected_components",
                "details.technical.cvss",
                "details.address",
            ]
        )
        data = {
            "title": "X",
            "affected_components": ["1.1.1.1", "10.0.0.1"],
            "details": {
                "address": "192.168.1.1",
                "technical": {"cvss": 9.8, "risk_level": "High"},
            },
        }
        result = excluder.remove_fields(data)

        # Parent structure and sibling fields preserved
        assert result == {
            "title": "X",
            "details": {
                "technical": {"risk_level": "High"},
            },
        }
        assert "affected_components" not in result
        assert "address" not in result["details"]
        assert "technical" in result["details"]
        assert "cvss" not in result["details"]["technical"]
        assert result["details"]["technical"]["risk_level"] == "High"


class TestFieldExcluderOriginalDataNotModified:
    """Test that the original data dictionary is not modified."""

    def test_original_data_unchanged(self):
        """Test that calling remove_fields doesn't modify the original data."""
        original_data = {
            "title": "X",
            "affected_components": ["1.1.1.1"],
        }
        excluder = FieldExcluder(exclude_fields=["affected_components"])
        result = excluder.remove_fields(original_data)

        # Original data should be unchanged
        assert original_data == {"title": "X", "affected_components": ["1.1.1.1"]}
        # Result should be modified
        assert result == {"title": "X"}
        assert "affected_components" not in result

    def test_deep_copy_independence(self):
        """Test that deeply nested structures are copied independently."""
        original_data = {
            "title": "X",
            "data": {
                "cvss": 9.8,
                "nested": {"deep": "value"},
            },
        }
        excluder = FieldExcluder(exclude_fields=["data.cvss"])
        result = excluder.remove_fields(original_data)

        # Original should be unchanged
        assert original_data["data"]["cvss"] == 9.8
        assert original_data["data"]["nested"]["deep"] == "value"

        # Result should be modified - cvss removed, parent and sibling preserved
        assert "cvss" not in result["data"]
        assert result["data"]["nested"]["deep"] == "value"


class TestParseRemoveFields:
    """Test scoped --remove-fields parsing."""

    def test_bare_name_defaults_to_finding(self):
        result, warnings = parse_remove_fields("affected_components,cvss")
        assert result == {"finding": ["affected_components", "cvss"]}
        assert warnings == []

    def test_empty_prefix_defaults_to_finding(self):
        result, warnings = parse_remove_fields(":cvss")
        assert result == {"finding": ["cvss"]}
        assert warnings == []

    def test_typed_specs(self):
        result, warnings = parse_remove_fields(
            "finding:cvss,note:icon_emoji,section:label"
        )
        assert result == {
            "finding": ["cvss"],
            "note": ["icon_emoji"],
            "section": ["label"],
        }
        assert warnings == []

    def test_dotted_path_after_colon(self):
        result, warnings = parse_remove_fields("finding:data.cvss")
        assert result == {"finding": ["data.cvss"]}
        assert warnings == []

    def test_unknown_type_warns_and_skips(self):
        result, warnings = parse_remove_fields("template:title,cvss")
        assert result == {"finding": ["cvss"]}
        assert len(warnings) == 1
        assert "unknown object type" in warnings[0]

    def test_empty_field_warns_and_skips(self):
        result, warnings = parse_remove_fields("note:")
        assert result == {}
        assert len(warnings) == 1
        assert "empty field name" in warnings[0]

    def test_format_remove_fields(self):
        formatted = format_remove_fields(
            {
                "finding": ["cvss", "affected_components"],
                "note": ["icon_emoji"],
            }
        )
        assert formatted == (
            "finding:cvss, finding:affected_components, note:icon_emoji"
        )


class TestFieldExcluderScoped:
    """Test object-type scoping."""

    def test_finding_exclusion_does_not_affect_notes(self):
        excluder = FieldExcluder(exclude_fields=["title", "id", "text"])
        note = {"id": "n1", "title": "Recon", "text": "body"}
        result = excluder.remove_fields(note, object_type="note")
        assert result == note

    def test_note_exclusion_only_applies_to_notes(self):
        excluder = FieldExcluder({"note": ["icon_emoji"]})
        note = {"id": "n1", "title": "Recon", "icon_emoji": "📝"}
        finding = {"id": "f1", "title": "X", "icon_emoji": "📝"}

        assert excluder.remove_fields(note, object_type="note") == {
            "id": "n1",
            "title": "Recon",
        }
        assert excluder.remove_fields(finding, object_type="finding") == finding

    def test_section_exclusion_only_applies_to_sections(self):
        excluder = FieldExcluder({"section": ["label"]})
        section = {"id": "exec", "label": "Executive Summary"}
        assert excluder.remove_fields(section, object_type="section") == {"id": "exec"}
        assert excluder.remove_fields(section, object_type="finding") == section

    def test_list_constructor_still_means_finding(self):
        excluder = FieldExcluder(exclude_fields=["affected_components"])
        data = {"title": "X", "affected_components": ["1.1.1.1"]}
        assert excluder.remove_fields(data) == {"title": "X"}
        assert excluder.remove_fields(data, object_type="note") == data
