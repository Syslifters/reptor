from unittest.mock import MagicMock

import pytest
from urllib3.util.retry import Retry

import reptor.settings as settings
from reptor.lib.reptor import Reptor

from ..APIClient import APIClient


class TestAPIClientSession:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.reptor = Reptor()
        self.reptor._config._raw_config["server"] = "https://demo.sysre.pt"
        self.reptor._config._raw_config["token"] = "sysreptor_test"
        self.client = APIClient(reptor=self.reptor, require_project_id=False)

    def test_build_session_mounts_retry_on_both_schemes(self):
        for scheme in ("http://demo.sysre.pt", "https://demo.sysre.pt"):
            adapter = self.client._session.get_adapter(scheme)
            retry = adapter.max_retries
            assert isinstance(retry, Retry)
            assert retry.total == settings.API_MAX_RETRIES
            assert retry.connect == settings.API_MAX_RETRIES
            assert retry.read == settings.API_MAX_RETRIES
            assert retry.status == settings.API_MAX_RETRIES
            assert retry.backoff_factor == settings.API_RETRY_BACKOFF_FACTOR
            assert list(retry.status_forcelist) == settings.API_RETRY_STATUS_FORCELIST
            # Never turn an exhausted status-retry into an exception here; the
            # existing response.raise_for_status() in _do_request owns that.
            assert retry.raise_on_status is False
            assert retry.respect_retry_after_header is True

    def test_prepare_kwargs_sets_defaults(self):
        prepared = self.client._prepare_kwargs({})
        assert prepared["timeout"] == settings.API_TIMEOUT
        assert prepared["verify"] is True  # insecure not set -> verify on
        assert prepared["allow_redirects"] is False

    def test_prepare_kwargs_respects_caller_overrides(self):
        prepared = self.client._prepare_kwargs({"timeout": 5, "verify": False})
        assert prepared["timeout"] == 5
        assert prepared["verify"] is False

    def test_api_timeout_from_config(self):
        self.reptor._config._raw_config["api_timeout"] = 90
        client = APIClient(reptor=self.reptor, require_project_id=False)
        assert client._prepare_kwargs({})["timeout"] == 90
        assert self.reptor.get_config().get_api_timeout_long() == 300

    def test_api_timeout_long_scales_with_config(self):
        self.reptor._config._raw_config["api_timeout"] = 600
        assert self.reptor.get_config().get_api_timeout() == 600
        assert self.reptor.get_config().get_api_timeout_long() == 600

    def test_insecure_config_disables_verify(self):
        self.reptor._config._raw_config["insecure"] = True
        client = APIClient(reptor=self.reptor, require_project_id=False)
        assert client._prepare_kwargs({})["verify"] is False

    def test_do_request_routes_through_session_with_defaults(self):
        response = MagicMock()
        response.headers = {}
        response.content = b"{}"
        self.client._session.get = MagicMock(return_value=response)

        self.client.get("https://demo.sysre.pt/api/v1/pentestprojects/")

        self.client._session.get.assert_called_once()
        _, kwargs = self.client._session.get.call_args
        assert kwargs["timeout"] == settings.API_TIMEOUT
        assert kwargs["verify"] is True
        assert kwargs["allow_redirects"] is False
