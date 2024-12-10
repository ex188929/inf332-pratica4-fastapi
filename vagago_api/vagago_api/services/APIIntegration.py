from ..models.Job import Job

class APIIntegration:
    api_name: str = None
    url: str = None

    def __init__(self, api_name: str, url: str):
        self.api_name = api_name
        self.url = url

    def get_data(self, query: dict) -> list[Job]:
        raise NotImplementedError
