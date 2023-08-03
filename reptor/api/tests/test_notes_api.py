import unittest

from reptor.lib.errors import MissingArgumentError
from reptor.lib.reptor import Reptor

from ..NotesAPI import NotesAPI


class TestNotesAPI(unittest.TestCase):
    def setUp(self):
        self.reptor = Reptor()

    def test_notes_api_init(self):
        # Test private note
        self.reptor._config._raw_config['server'] = 'https://demo.sysre.pt'
        self.reptor._config._raw_config['cli'] = {'private_note': True}
        try:
            n = NotesAPI(reptor=self.reptor)
            self.assertTrue(n.private_note)
        except (ValueError, MissingArgumentError):
            self.fail("NotesAPI raised Error")

        # Test project note
        self.reptor._config._raw_config['server'] = 'https://demo.sysre.pt'
        self.reptor._config._raw_config['cli'] = {'private_note': False}
        self.reptor._config._raw_config['project_id'] = '8a6ebd7b-637f-4f38-bfdd-3e8e9a24f64e'
        try:
            n = NotesAPI(reptor=self.reptor)
            self.assertFalse(n.private_note)
        except (ValueError, MissingArgumentError):
            self.fail("NotesAPI raised Error")

        # Test note without project id and private_note
        self.reptor._config._raw_config['server'] = 'https://demo.sysre.pt'
        self.reptor._config._raw_config['cli'] = {'private_note': False}
        self.reptor._config._raw_config['project_id'] = ''
        with self.assertRaises(MissingArgumentError):
            NotesAPI(reptor=self.reptor)
            
