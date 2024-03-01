import json
import os
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from reptor.api.APIClient import APIClient
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

        finding_data = json.loads(
            open(
                os.path.join(os.path.dirname(__file__), f"./data/finding_data.json")
            ).read()
        )
        url = "http://localhost:8080"

        # Test Defect Dojo API key
        dd_apikey = "ef8d9jd996b8p17534383cbte26red188d59c4bs"

        DefectDojo.DefectDojo.apikey = dd_apikey

        APIClient.get = MagicMock(return_value=MockResponse(finding_data, 200))
        defectdojo = DefectDojo.DefectDojo(reptor=self.reptor, url=url)

        assert finding_data == defectdojo._get_defectdojo_findings()
