from api.APIClient import APIClient


class TemplatesAPI(APIClient):

    endpoint = f"api/v1/findingtemplates/"

    def __init__(self) -> None:
        super().__init__()
