from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from reptor.lib.reptor import reptor
from reptor.models.Note import Note, NoteTemplate

from ..NotesAPI import NotesAPI


class TestNotesAPI:
    class MockResponse:
        def __init__(self, content, status_code, raise_exception=False):
            self.content = content
            self.status_code = status_code
            self.raise_exception = raise_exception

        def raise_for_status(self):
            if self.raise_exception:
                raise HTTPError("Mocked HTTPError")
            return

        def json(self):
            return self.content

    test_note = {
        "id": "51abd3d3-803e-43a5-aa25-bf30b7fbf70a",
        "created": "2023-09-07T14:00:32.777492Z",
        "updated": "2023-09-07T14:00:45.409725Z",
        "title": "My Note",
        "text": "My Content",
        "checked": None,
        "icon_emoji": "\ud83d\udd25",
        "order": 4,
        "parent": "8880ce39-90ed-4383-9320-d5d74b1ae34f",
    }

    @pytest.fixture(autouse=True)
    def setUp(self):
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["personal_note"] = True
        self.notes = NotesAPI(reptor=reptor)
        self.uploaded = []
        self.notes._upload_note = MagicMock(
            side_effect=lambda note, **kwargs: self.uploaded.append(note)
        )

    def _existing_note(self, text) -> Note:
        """Make get_note() return a stored note with the given text."""
        note = Note(dict(self.test_note, text=text))
        self.notes.get_note = MagicMock(return_value=note)
        return note

    def _mock_methods(self):
        self.notes.get_or_create_note_by_title = MagicMock(
            return_value=Note(self.test_note)
        )
        self.notes.create_note = MagicMock(return_value=Note(self.test_note))
        self.notes.put = MagicMock(return_value=self.MockResponse("", 201))

    def test_write_note_appends_by_default(self):
        note = self._existing_note("Existing")
        result = self.notes.write_note(id=note.id, text="New", timestamp=False)

        assert self.uploaded[0].text == "Existing\n\nNew"
        assert result is self.uploaded[0]
        assert result.text == "Existing\n\nNew"

    def test_write_note_overwrite_replaces_text(self):
        note = self._existing_note("Existing")
        self.notes.write_note(id=note.id, text="New", timestamp=False, overwrite=True)

        assert self.uploaded[0].text == "New"

    def test_write_note_overwrite_expresses_checklist_state_change(self):
        note = self._existing_note("- [ ] Recon\n- [ ] Exploit")
        self.notes.write_note(
            id=note.id,
            text="- [x] Recon\n- [ ] Exploit",
            timestamp=False,
            overwrite=True,
        )

        # The flipped checklist replaces the old one instead of accumulating
        # a second copy showing the previous state.
        assert self.uploaded[0].text == "- [x] Recon\n- [ ] Exploit"
        assert self.uploaded[0].text.count("Recon") == 1

    def test_write_note_overwrite_with_timestamp_drops_old_text(self):
        note = self._existing_note("Old")
        self.notes.write_note(id=note.id, text="New", timestamp=True, overwrite=True)

        text = self.uploaded[0].text
        assert "Old" not in text
        assert text.startswith("[")
        assert text.endswith("New")

    def test_write_note_overwrite_on_empty_note_is_unchanged(self):
        note = self._existing_note("")
        self.notes.write_note(id=note.id, text="New", timestamp=False, overwrite=True)

        assert self.uploaded[0].text == "New"

    def test_write_note_by_id_ignores_title(self):
        note = self._existing_note("Existing")
        self.notes.write_note(
            id=note.id,
            title="Different Title",
            text="New",
            timestamp=False,
        )

        assert self.uploaded[0].title == "My Note"
        assert self.uploaded[0].text == "Existing\n\nNew"

    def test_rename_note(self):
        note = self._existing_note("Existing content")
        result = self.notes.rename_note(note_id=note.id, title="Renamed")

        assert self.uploaded[0].title == "Renamed"
        assert self.uploaded[0].text == "Existing content"
        assert result is self.uploaded[0]

    def test_rename_note_not_found(self):
        self.notes.get_note = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="does not exist"):
            self.notes.rename_note(note_id="missing", title="New Title")

    def test_write_note_templates_overwrite_propagates_to_children(self):
        parent = Note(dict(self.test_note, text="Parent old"))
        child = Note(dict(self.test_note, id="child-id", text="Child old"))
        self.notes.get_note = MagicMock(
            side_effect=lambda id=None, title=None: (
                child if id == "child-id" else parent
            )
        )

        template = NoteTemplate.from_kwargs(id=parent.id, text="Parent new")
        template.children = [NoteTemplate.from_kwargs(id="child-id", text="Child new")]
        result = self.notes.write_note_templates(
            template, timestamp=False, overwrite=True
        )

        assert [n.text for n in self.uploaded] == ["Parent new", "Child new"]
        assert result is self.uploaded[0]
        assert result.text == "Parent new"

    def test_notes_api_init(self):
        # Test valid personal note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["personal_note"] = True
        try:
            n = NotesAPI(reptor=reptor)
            assert n.personal_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test valid project note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["personal_note"] = False
        reptor._config._raw_config["project_id"] = (
            "2b5de38d-2932-4112-b0f7-42c4889dd64d"
        )
        try:
            n = NotesAPI(reptor=reptor)
            assert not n.personal_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test missing project id and missing personal_note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["personal_note"] = False
        reptor._config._raw_config["project_id"] = ""
        with pytest.raises(ValueError):
            NotesAPI(reptor=reptor)

        # Test missing server
        reptor._config._raw_config["server"] = ""
        reptor._config._raw_config["personal_note"] = True
        with pytest.raises(ValueError):
            NotesAPI(reptor=reptor)
