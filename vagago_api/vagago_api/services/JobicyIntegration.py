import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job


class JobicyIntegration(APIIntegration):
    def __init__(self):
        super().__init__("Jobicy", "https://jobicy.com/api/v2/remote-jobs")

    def get_data(self, query: dict) -> list[Job]:
        # TODO validate queries
        response = requests.get(self.url, params=query)
        response_obj = response.json()
        jobs = []
        for job in response_obj["jobs"]:
            new_job = Job(
                external_id=job["id"],
                title=job["jobTitle"],
                description=job["jobDescription"],
                level=job["jobLevel"],
                location=job["jobGeo"],
                job_type=job["jobType"],
                company_name=job["companyName"],
                published_date=job["pubDate"],
                url=job["url"],
            )
            jobs.append(new_job)

        return jobs
