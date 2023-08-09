import pytest

from reptor.lib.errors import MissingArgumentError
from reptor.lib.reptor import Reptor

from ..NotesAPI import NotesAPI


class TestNotesAPI:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()

    def test_notes_api_init(self):
        # Test valid private note
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": True}
        try:
            n = NotesAPI(reptor=self.reptor)
            assert n.private_note
        except (ValueError, MissingArgumentError):
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
        except (ValueError, MissingArgumentError):
            self.fail("NotesAPI raised Error")

        # Test missing project id and missing private_note
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["cli"] = {"private_note": False}
        self.reptor._config._raw_config["project_id"] = ""
        with pytest.raises(MissingArgumentError):
            NotesAPI(reptor=self.reptor)

        # Test missing server
        self.reptor._config._raw_config["server"] = ""
        self.reptor._config._raw_config["cli"] = {"private_note": True}
        with pytest.raises(ValueError):
            NotesAPI(reptor=self.reptor)
