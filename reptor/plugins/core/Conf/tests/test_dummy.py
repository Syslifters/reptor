import pytest


@pytest.mark.integration
class TestDummy(object):
    # Needed to run conftest
    def test_dummy(self):
        pass
