unittest:
	pytest -k "not integration"

integrationtest:
	pytest -k integration