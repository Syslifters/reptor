import inspect

import pytest
from unittest.mock import MagicMock, patch
from reptor.plugins.core.Mcp.Logic import McpLogic
from reptor.plugins.core.Mcp.FieldExcluder import FieldExcluder
from reptor.plugins.core.Mcp.Server import MCPServer


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

    @pytest.mark.parametrize("invalid_limit", [0, -1])
    def test_list_notes_invalid_limit_raises(self, mock_reptor, sample_notes, invalid_limit):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        with pytest.raises(ValueError, match="limit must be a positive integer"):
            logic.list_notes(limit=invalid_limit)

    def test_list_notes_tree_order(self, mock_reptor):
        from reptor.models.Note import Note

        notes = [
            Note({"id": "child-b2", "title": "Child B2", "parent": "root-b", "order": 2}),
            Note({"id": "root-b", "title": "Root B", "parent": None, "order": 2}),
            Note({"id": "child-a1", "title": "Child A1", "parent": "root-a", "order": 1}),
            Note({"id": "root-a", "title": "Root A", "parent": None, "order": 1}),
            Note({"id": "child-b1", "title": "Child B1", "parent": "root-b", "order": 1}),
            Note({"id": "child-a2", "title": "Child A2", "parent": "root-a", "order": 2}),
        ]
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = notes

        results = logic.list_notes()

        assert [note["id"] for note in results] == [
            "root-a",
            "child-a1",
            "child-a2",
            "root-b",
            "child-b1",
            "child-b2",
        ]

    def test_list_notes_limit_respects_tree_order(self, mock_reptor):
        from reptor.models.Note import Note

        notes = [
            Note({"id": "root-b", "title": "Root B", "parent": None, "order": 2}),
            Note({"id": "root-a", "title": "Root A", "parent": None, "order": 1}),
        ]
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.get_notes.return_value = notes

        results = logic.list_notes(limit=1)

        assert len(results) == 1
        assert results[0]["id"] == "root-a"

    def test_list_notes_field_exclusion(self, mock_reptor, sample_notes):
        excluder = FieldExcluder({"note": ["icon_emoji"]})
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=excluder)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        results = logic.list_notes()

        assert "icon_emoji" not in results[0]
        assert results[0]["title"] == "Recon"

    def test_list_notes_finding_exclusion_does_not_strip_note_fields(
        self, mock_reptor, sample_notes
    ):
        excluder = FieldExcluder(exclude_fields=["title", "id", "text"])
        logic = McpLogic(reptor_instance=mock_reptor, field_excluder=excluder)
        mock_reptor.api.notes.get_notes.return_value = sample_notes

        results = logic.list_notes()

        assert results[0]["id"] == "n1"
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
        excluder = FieldExcluder({"note": ["icon_emoji"]})
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
        mock_reptor.api.notes.write_note.return_value = sample_note

        result = logic.write_note(title="Recon", text="more text")

        mock_reptor.api.notes.write_note.assert_called_once_with(
            id=None,
            title="Recon",
            text="more text",
            parent_title=None,
            timestamp=False,
            overwrite=False,
        )
        assert result["id"] == "n1"
        mock_reptor.api.notes.get_note.assert_not_called()

    def test_write_note_append_by_id(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = sample_note

        result = logic.write_note(note_id="n1", text="appended")

        call_kwargs = mock_reptor.api.notes.write_note.call_args.kwargs
        assert call_kwargs["id"] == "n1"
        assert call_kwargs["text"] == "appended"
        assert result["id"] == "n1"
        mock_reptor.api.notes.get_note.assert_not_called()

    def test_write_note_returns_status_when_write_returns_none(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = None

        result = logic.write_note(title="New", text="hi")

        assert result["status"] == "written"
        assert result["title"] == "New"
        mock_reptor.api.notes.get_note.assert_not_called()

    def test_write_note_requires_argument(self, mock_reptor):
        logic = McpLogic(reptor_instance=mock_reptor)

        with pytest.raises(ValueError, match="note_id or title"):
            logic.write_note(text="orphan")

    def test_write_note_defaults_to_appending(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = sample_note

        logic.write_note(title="Recon", text="more")

        assert mock_reptor.api.notes.write_note.call_args.kwargs["overwrite"] is False

    def test_write_note_forwards_overwrite(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = sample_note

        logic.write_note(note_id="n1", text="- [x] Recon", overwrite=True)

        assert mock_reptor.api.notes.write_note.call_args.kwargs["overwrite"] is True

    def test_write_note_by_id_does_not_forward_title(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        mock_reptor.api.notes.write_note.return_value = sample_note

        logic.write_note(note_id="n1", title="Wrong Title", text="appended")

        call_kwargs = mock_reptor.api.notes.write_note.call_args.kwargs
        assert call_kwargs["id"] == "n1"
        assert call_kwargs["title"] is None
        assert call_kwargs["text"] == "appended"

    def test_rename_note(self, mock_reptor, sample_note):
        logic = McpLogic(reptor_instance=mock_reptor)
        renamed = sample_note
        renamed.title = "Renamed"
        mock_reptor.api.notes.rename_note.return_value = renamed

        result = logic.rename_note(note_id="n1", title="Renamed")

        mock_reptor.api.notes.rename_note.assert_called_once_with(
            note_id="n1", title="Renamed"
        )
        assert result["title"] == "Renamed"
        assert result["id"] == "n1"


def _registered_tool(server, name):
    """Pull a tool function out of the patched FastMCP registration calls."""
    for call in server.mcp.tool.return_value.call_args_list:
        fn = call.args[0]
        if fn.__name__ == name:
            return fn
    raise AssertionError(f"tool {name!r} was not registered")


class TestMCPWriteNoteTool:
    """The MCP tool must expose overwrite so a model can replace note content."""

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_tool_exposes_overwrite_defaulting_to_append(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP")

        params = inspect.signature(_registered_tool(server, "reptor_write_note")).parameters
        assert "overwrite" in params
        assert params["overwrite"].default is False

    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_tool_forwards_overwrite_to_logic(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP")
        write_note = _registered_tool(server, "reptor_write_note")
        server.logic = MagicMock()

        write_note(title="Checklist", text="- [x] Recon", overwrite=True)

        assert server.logic.write_note.call_args.kwargs["overwrite"] is True


class TestMCPRenameNoteTool:
    @patch("reptor.plugins.core.Mcp.Server.FastMCP")
    def test_rename_note_tool_registered(self, mock_fast_mcp):
        server = MCPServer(name="ReptorMCP")
        rename_note = _registered_tool(server, "reptor_rename_note")
        server.logic = MagicMock()

        rename_note(note_id="n1", title="Renamed")

        server.logic.rename_note.assert_called_once_with(
            note_id="n1", title="Renamed"
        )
