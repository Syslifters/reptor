from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from reptor.lib.exceptions import LockedException
from reptor.lib.reptor import Reptor
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
        "lock_info": None,
        "title": "My Note",
        "text": "My Content",
        "checked": None,
        "icon_emoji": "\ud83d\udd25",
        "status_emoji": None,
        "order": 4,
        "parent": "8880ce39-90ed-4383-9320-d5d74b1ae34f",
    }
    locked_note = {
        "id": "1c76a78f-472c-445f-993a-214b86a05a49",
        "created": "2023-09-06T19:52:55.772872Z",
        "updated": "2023-09-06T19:52:56.475750Z",
        "lock_info": {
            "created": "2023-09-07T16:52:11.215893Z",
            "updated": "2023-09-07T16:52:11.216099Z",
            "last_ping": "2023-09-07T16:52:11.215905Z",
            "expires": "2023-09-07T16:53:41.215905Z",
            "user": {
                "id": "f18706c8-bff2-4526-b462-48d6c0f94d92",
                "username": "timmi",
                "name": "",
                "title_before": None,
                "first_name": "",
                "middle_name": None,
                "last_name": "",
                "title_after": None,
                "is_active": True,
            },
        },
        "title": "My Note",
        "text": "[2023-09-06 21:52:56]\n*Upload me*",
        "checked": None,
        "icon_emoji": None,
        "status_emoji": None,
        "order": 1,
        "parent": "4a071c2a-32fc-40bc-8157-54b4e944541f",
        "assignee": None,
    }

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": True}
        self.notes = NotesAPI(reptor=self.reptor)

    def _mock_methods(self):
        self.notes.get_or_create_note_by_title = MagicMock(
            return_value=Note(self.test_note)
        )
        self.notes.put = MagicMock(return_value=self.MockResponse("", 201))
        self.notes._do_unlock = MagicMock(return_value=self.MockResponse("", 200))

    def test_write_notes_lock(self):
        # Note locked by self user without force_unlock
        self._mock_methods()
        self.notes._do_lock = MagicMock(
            return_value=self.MockResponse(self.locked_note, 200)
        )
        self.notes.get_notes = MagicMock()
        with pytest.raises(LockedException):
            self.notes.write_note(text="content", force_unlock=False)
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 0
        assert self.notes._do_unlock.call_count == 0

        # Note locked by self user with force_unlock
        self._mock_methods()
        self.notes._do_lock = MagicMock(
            return_value=self.MockResponse(self.locked_note, 200)
        )
        self.notes.write_note(text="content", force_unlock=True)
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 1
        assert self.notes._do_unlock.call_count == 1

        # Note unlocked without force_unlock
        self._mock_methods()
        self.notes._do_lock = MagicMock(
            return_value=self.MockResponse(self.locked_note, 201)
        )
        self.notes.write_note(text="content", force_unlock=False)
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 1
        assert self.notes._do_unlock.call_count == 1

        # Note unlocked with force_unlock
        self._mock_methods()
        self.notes._do_lock = MagicMock(
            return_value=self.MockResponse(self.locked_note, 201)
        )
        self.notes.write_note("content", force_unlock=True)
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 1
        assert self.notes._do_unlock.call_count == 1

        # Note locked by other user without force_unlock
        self._mock_methods()
        exception = HTTPError("Raise for status 403")
        exception.response = self.MockResponse(self.locked_note, 403)
        self.notes._do_lock = MagicMock(side_effect=exception)

        with pytest.raises(LockedException) as e:
            self.notes.write_note(text="content", force_unlock=False)
        assert str(e.value) == "Cannot unlock. Locked by @timmi."
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 0
        assert self.notes._do_unlock.call_count == 0

        # Note locked by other user with force_unlock
        self._mock_methods()
        exception = HTTPError("Raise for status 403")
        exception.response = self.MockResponse(self.locked_note, 403)
        self.notes._do_lock = MagicMock(side_effect=exception)

        with pytest.raises(LockedException) as e:
            self.notes.write_note(text="content", force_unlock=True)
        assert str(e.value) == "Cannot unlock. Locked by @timmi."
        assert self.notes.get_or_create_note_by_title.call_count == 1
        assert self.notes._do_lock.call_count == 1
        assert self.notes.put.call_count == 0
        assert self.notes._do_unlock.call_count == 0

    def test_notes_api_init(self):
        # Test valid personal note
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": True}
        try:
            n = NotesAPI(reptor=self.reptor)
            assert n.private_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test valid project note
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": False}
        self.reptor._config._raw_config[
            "project_id"
        ] = "2b5de38d-2932-4112-b0f7-42c4889dd64d"
        try:
            n = NotesAPI(reptor=self.reptor)
            assert not n.private_note
        except ValueError:
            self.fail("NotesAPI raised Error")

        # Test missing project id and missing private_note
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": False}
        self.reptor._config._raw_config["project_id"] = ""
        with pytest.raises(ValueError):
            NotesAPI(reptor=self.reptor)

        # Test missing server
        self.reptor._config._raw_config["server"] = ""
        self.reptor._config._raw_config["cli"] = {"private_note": True}
        with pytest.raises(ValueError):
            NotesAPI(reptor=self.reptor)
