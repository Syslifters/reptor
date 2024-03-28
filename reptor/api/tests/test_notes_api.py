from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from reptor.lib.reptor import reptor
from reptor.models.Note import Note

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
        "status_emoji": None,
        "order": 4,
        "parent": "8880ce39-90ed-4383-9320-d5d74b1ae34f",
    }

    @pytest.fixture(autouse=True)
    def setUp(self):
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["cli"] = {"private_note": True}
        self.notes = NotesAPI(reptor=reptor)

    def _mock_methods(self):
        self.notes.get_or_create_note_by_title = MagicMock(
            return_value=Note(self.test_note)
        )
        self.notes.create_note = MagicMock(return_value=Note(self.test_note))
        self.notes.put = MagicMock(return_value=self.MockResponse("", 201))

    def test_notes_api_init(self):
        # Test valid personal note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["cli"] = {"private_note": True}
        try:
            n = NotesAPI(reptor=reptor)
            assert n.private_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test valid project note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["cli"] = {"private_note": False}
        reptor._config._raw_config["project_id"] = (
            "2b5de38d-2932-4112-b0f7-42c4889dd64d"
        )
        try:
            n = NotesAPI(reptor=reptor)
            assert not n.private_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test missing project id and missing private_note
        reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        reptor._config._raw_config["cli"] = {"private_note": False}
        reptor._config._raw_config["project_id"] = ""
        with pytest.raises(ValueError):
            NotesAPI(reptor=reptor)

        # Test missing server
        reptor._config._raw_config["server"] = ""
        reptor._config._raw_config["cli"] = {"private_note": True}
        with pytest.raises(ValueError):
            NotesAPI(reptor=reptor)
