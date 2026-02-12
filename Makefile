unittest:
	pytest -k "not integration"

integrationtest:
	pytest -k integration -p reptor.plugins.core.Conf.tests.conftest