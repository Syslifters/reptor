import pytest
from unittest.mock import MagicMock
from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder


class TestMCPNotesRead:
    """Tests for the read-only notes tools."""

    def test_list_notes_summary(self, mock_reptor, sample_notes):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        results = logic.list_notes()

        assert len(results) == 2
        assert results[0] == {
            "id": "n1",
            "title": "Recon",
            "parent": None,
            "order": 1,
            "checked": None,
            "icon_emoji": "📝",
        }
        assert results[1]["id"] == "n2"
        assert results[1]["parent"] == "n1"
        # Summary must not leak the full note text
        assert "text" not in results[0]
        mock_reptor.api.projects.init_project.assert_called_with("test-project-id")
        mock_reptor.api.notes.get_notes.assert_called_once()

    def test_list_notes_limit(self, mock_reptor, sample_notes):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        results = logic.list_notes(limit=1)

        assert len(results) == 1
        assert results[0]["id"] == "n1"

    def test_list_notes_field_exclusion(self, mock_reptor, sample_notes):
        excluder = FieldExcluder(exclude_fields=["icon_emoji"])
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=excluder)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        results = logic.list_notes()

        assert "icon_emoji" not in results[0]
        assert results[0]["title"] == "Recon"

    def test_list_notes_empty(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = []

        assert logic.list_notes() == []

    def test_get_note_by_id(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_note.return_value = sample_note

        result = logic.get_note(note_id="n1")

        assert result["id"] == "n1"
        assert result["text"] == "Nmap shows 22/tcp and 443/tcp open."
        mock_reptor.api.notes.get_note.assert_called_once_with(id="n1", title=None)

    def test_get_note_by_title(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_note.return_value = sample_note

        result = logic.get_note(title="Recon")

        assert result["title"] == "Recon"
        mock_reptor.api.notes.get_note.assert_called_once_with(id=None, title="Recon")

    def test_get_note_field_exclusion(self, mock_reptor, sample_note):
        excluder = FieldExcluder(exclude_fields=["icon_emoji"])
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=excluder)
        mock_reptor.api.notes.get_note.return_value = sample_note

        result = logic.get_note(note_id="n1")

        assert "icon_emoji" not in result
        assert result["id"] == "n1"

    def test_get_note_not_found(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_note.return_value = None

        with pytest.raises(ValueError, match="Note not found"):
            logic.get_note(note_id="missing")

    def test_get_note_requires_argument(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="note_id or title"):
            logic.get_note()

    def test_get_note_no_project(self):
        mock_reptor = MagicMock()
        mock_reptor.get_active_project_id.return_value = ""
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="No project configured"):
            logic.get_note(note_id="n1")


class TestMCPNotesWrite:
    """Tests for the note write tool."""

    def test_write_note_create_by_title(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = None
        mock_reptor.api.notes.get_note.return_value = sample_note

        result = logic.write_note(title="Recon", text="more text")

        mock_reptor.api.notes.write_note.assert_called_once_with(
            id=None,
            title="Recon",
            text="more text",
            parent_title=None,
            timestamp=False,
        )
        assert result["id"] == "n1"

    def test_write_note_append_by_id(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = None
        mock_reptor.api.notes.get_note.return_value = sample_note

        result = logic.write_note(note_id="n1", text="appended")

        call_kwargs = mock_reptor.api.notes.write_note.call_args.kwargs
        assert call_kwargs["id"] == "n1"
        assert call_kwargs["text"] == "appended"
        assert result["id"] == "n1"

    def test_write_note_returns_status_when_not_refetchable(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = None
        mock_reptor.api.notes.get_note.return_value = None

        result = logic.write_note(title="New", text="hi")

        assert result["status"] == "written"
        assert result["title"] == "New"

    def test_write_note_requires_argument(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="note_id or title"):
            logic.write_note(text="orphan")
