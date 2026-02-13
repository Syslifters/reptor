unittest:
	pytest -k "not integration"

integrationtest:
	pytest -k integration --import-mode=importlib -p reptor.plugins.core.Conf.tests.conftest