import pathlib

import pytest
import yaml
import os


@pytest.mark.integration
class TestIntegrationConf(object):
    def test_config_file(self):
        # Assert config file was created correctly
        with open(pathlib.Path.home() / ".sysreptor/config.yaml") as f:
            config = yaml.safe_load(f)
        assert config["server"] == os.environ.get("SYSREPTOR_SERVER", "")
        assert config["token"] == os.environ.get("SYSREPTOR_API_TOKEN", "")
        assert config["project_id"] is None
