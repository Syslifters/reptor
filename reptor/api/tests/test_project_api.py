import unittest

from reptor.lib.reptor import Reptor

from ..ProjectsAPI import ProjectsAPI


class TestProjectsAPI(unittest.TestCase):
    def setUp(self):
        self.reptor = Reptor()

    def test_project_api_init(self):
        # Test valid init
        self.reptor._config._raw_config['server'] = 'https://demo.sysre.pt'
        self.reptor._config._raw_config['project_id'] = '123456789'
        try:
            ProjectsAPI(reptor=self.reptor)
        except ValueError:
            self.fail("ProjectsAPI raised ValueError")

        # Test missing server
        self.reptor._config._raw_config['server'] = ''
        with self.assertRaises(ValueError):
            ProjectsAPI(reptor=self.reptor)

        # Test missing project id
        self.reptor._config._raw_config['server'] = 'https://demo.sysre.pt'
        self.reptor._config._raw_config['project_id'] = ''
        with self.assertRaises(ValueError):
            ProjectsAPI(reptor=self.reptor)
