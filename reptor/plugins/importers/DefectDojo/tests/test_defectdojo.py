import json
import os
from unittest.mock import MagicMock

import pytest
import requests
from requests.exceptions import HTTPError

from reptor.lib.conf import Config
from reptor.lib.reptor import reptor

from .. import DefectDojo


class TestDefectDojo:
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

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = reptor
        self.reptor._config = Config()
        self.reptor._config._raw_config = {}

    def test_init(self):
        self.reptor.get_config()
        with pytest.raises(ValueError):
            # Should raise because of missing URL
            DefectDojo.DefectDojo()

        with pytest.raises(ValueError):
            # Should raise because of missing API key
            DefectDojo.DefectDojo(url="test")

    def test_run(self):
        finding_data = json.loads(
            open(
                os.path.join(os.path.dirname(__file__), f"./data/finding_data.json")
            ).read()
        )
        url = "http://localhost:8080"

        # Test Defect Dojo API key
        dd_apikey = "ef8d9jd996b8p17534383cbte26red188d59c4bs"
        DefectDojo.DefectDojo.apikey = dd_apikey

        requests.get = MagicMock(return_value=self.MockResponse(finding_data, 200))
        defectdojo = DefectDojo.DefectDojo(url=url)
        defectdojo._upload_finding_template = MagicMock()

        defectdojo.run()

        defectdojo._upload_finding_template.assert_called_once()
        uploaded_finding = defectdojo._upload_finding_template.call_args.args[0]
        assert (
            uploaded_finding.translations[0].data.title
            == "AVD-AWS-0107 - An Ingress Security Group Rule Allows Traffic From /0."
        )

    def test_get_findings(self):
        finding_data = json.loads(
            open(
                os.path.join(os.path.dirname(__file__), f"./data/finding_data.json")
            ).read()
        )
        url = "http://localhost:8080"

        # Test Defect Dojo API key
        dd_apikey = "ef8d9jd996b8p17534383cbte26red188d59c4bs"
        DefectDojo.DefectDojo.apikey = dd_apikey

        requests.get = MagicMock(return_value=self.MockResponse(finding_data, 200))
        defectdojo = DefectDojo.DefectDojo(url=url)

        assert finding_data == defectdojo._get_defectdojo_findings()
