import os

import pytest

from reptor.lib.plugins.TestCaseToolPlugin import TestCaseToolPlugin

from ..Toolbase import MYMODULENAME


class TestMyModule(TestCaseToolPlugin):
    templates_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../templates")
    )

    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        MYMODULENAME.set_template_vars(
            os.path.dirname(self.templates_path), skip_user_plugins=True
        )
        self.mymodule = MYMODULENAME(reptor=self.reptor)

    def _load_xml_data(self, xml_file):
        self.mymodule.input_format = "xml"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{xml_file}")
        with open(filepath, "r") as f:
            self.mymodule.raw_input = f.read()

    def _load_json_data(self, json_file):
        self.mymodule.input_format = "json"
        filepath = os.path.join(os.path.dirname(__file__), f"./data/{json_file}")
        with open(filepath, "r") as f:
            self.mymodule.raw_input = f.read()

    def test_true_example(self):
        assert True == True
        raise NotImplementedError("Test not implemented")
