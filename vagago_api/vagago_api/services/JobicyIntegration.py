import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job


# from enum import Enum

valid_locations = [
    "apac",
    "emea",
    "latam",
    "argentina",
    "australia",
    "austria",
    "belgium",
    "brazil",
    "bulgaria",
    "canada",
    "china",
    "costa-rica",
    "croatia",
    "cyprus",
    "czechia",
    "denmark",
    "estonia",
    "europe",
    "finland",
    "france",
    "germany",
    "greece",
    "hungary",
    "ireland",
    "israel",
    "italy",
    "japan",
    "latvia",
    "lithuania",
    "mexico",
    "netherlands",
    "new-zealand",
    "norway",
    "philippines",
    "poland",
    "portugal",
    "romania",
    "singapore",
    "slovakia",
    "slovenia",
    "south-korea",
    "spain",
    "sweden",
    "switzerland",
    "thailand",
    "turkiye",
    "united-arab-emirates",
    "uk",
    "usa",
    "vietnam",
]


class JobicyIntegration(APIIntegration):
    def __init__(self):
        super().__init__("Jobicy", "https://jobicy.com/api/v2/remote-jobs")

    def validate_location(self, location_query: str) -> str:
        print(
            "Jobicy only accepts one parameter for location, so we will return the first valid location found."
        )
        for loc in location_query.split(","):
            if loc in valid_locations:
                return loc
        return "brazil"

    def get_data(self, query: dict) -> list[Job]:
        # TODO validate queries
        print("Calling Jobicy API at ", self.url, " with query ", query)
        response = requests.get(self.url, params=query, timeout=10)
        response_obj = response.json()
        jobs = []

        # handle empty responses
        iserror = isinstance(response_obj["jobs"], dict)
        if iserror:
            return jobs

        # parse response for status code 200
        for job in response_obj["jobs"]:
            new_job = Job(
                external_id=job["id"],
                title=job.get("jobTitle", ""),
                required_skills=[],  # TODO: parse description with LLM
                level=job.get("jobLevel", ""),
                location=job.get("jobGeo", []),
                salary_min=job.get("annualSalaryMin", None),
                salary_max=job.get("annualSalaryMax", None),
                salary_currency=job.get("salaryCurrency", None),
                description=job.get("jobDescription", ""),
                job_type=job.get("jobType", []),
                company_name=job.get("companyName", ""),
                published_date=job.get("pubDate", None),
                url=job.get("url", ""),
            )
            jobs.append(new_job)

        return jobs
