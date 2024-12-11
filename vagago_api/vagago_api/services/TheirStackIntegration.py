import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job
from vivago_api.settings import THEIRSTACK_API_KEY

class TheirStackIntegration(APIIntegration):
    def __init__(self):
        super().__init__("TheirStack", "https://api.theirstack.com/v1/jobs")

    def get_data(self, query: dict) -> list[Job]:
        # parse params
        params = {
            "count": query.get("count", 10),
            "term": query.get("term", ""),
            "location": query.get("location", "Brazil")
        }

        # get response
        headers = {
            "Authorization": f"Bearer {THEIRSTACK_API_KEY}",
            "accept": "application/json"
        }
        response = requests.get(
            self.url,
            params=params,
            headers=headers,
            timeout=100,
        )
        response_obj = response.json()
        jobs = []

        # parse response for status code 200
        if response.status_code == 200:
            for job in response_obj.get("jobs", []):
                new_job = Job(
                    external_id=job["id"],
                    title=job.get("title", ""),
                    required_skills=job.get("skills", []),
                    level=job.get("level", ""),
                    location=job.get("location", ""),
                    salary_min=job.get("salary_min", None),
                    salary_max=job.get("salary_max", None),
                    salary_currency=job.get("salary_currency", ""),
                    description=job.get("description", ""),
                    job_type=job.get("job_type", []),
                    company_name=job.get("company_name", ""),
                    published_date=job["published_date"],
                    url=job.get("url", ""),
                )
                jobs.append(new_job)
        else:
            response.raise_for_status()

        return jobs
