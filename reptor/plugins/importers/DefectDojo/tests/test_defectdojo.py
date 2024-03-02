import json

import pytest

import requests_mock

from reptor.lib.conf import Config
from reptor.lib.reptor import Reptor

from .. import DefectDojo


class TestDefectDojo:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config = Config()
        self.reptor._config._raw_config = {}

    def test_init(self):
        self.reptor.get_config()
        with pytest.raises(ValueError):
            # Should raise because of missing URL
            DefectDojo.DefectDojo(reptor=self.reptor)

        with pytest.raises(ValueError):
            # Should raise because of missing API key
            DefectDojo.DefectDojo(reptor=self.reptor, url="test")

        DefectDojo.DefectDojo.apikey = "test"
        DefectDojo.DefectDojo(reptor=self.reptor, url="test")

    def test_get_findings(self):
        finding_data = json.loads(
            open("./assets/finding_data.json").read()
        )
        url="http://localhost:8080"

        class Client:
            def __init__(*args, **kwargs):
                pass

            def execute(self, *args, **kwargs):
                return finding_data

        # Test Defect Dojo API key
        dd_apikey = "ef8d9jd996b8p17534383cbte26red188d59c4bs"

        DefectDojo.DefectDojo.apikey = dd_apikey
        requests_mock.get(f'{url}/api/v2/findings', json=finding_data)
        defectdojo = DefectDojo.DefectDojo(
            reptor=self.reptor, url=url
        )
        assert finding_data == defectdojo._get_ghostwriter_findings()
