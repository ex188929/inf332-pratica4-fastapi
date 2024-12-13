import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job


class TheirStackIntegration(APIIntegration):
    def __init__(self):
        super().__init__(
            "TheirStack", "https://api.theirstack.com/v1/jobs/search"
        )

    def get_data(self, query: dict) -> list[Job]:
        """Get Data from API.

        Args:
            query (dict): dict with args:
                title
                required_skills
                location
                contracttype
                salary_min
                salary_max
                salary_currency
                description
                company_name
                industry
                count

        Returns:
            list[Job]: List of Jobs returned by API.
        """
        # parse params
        payload = {
            "offset": 0,
            "page": 0,
            "posted_at_max_age_days": 365,
            "limit": query.get("count", 10),
            "job_description_pattern_is_case_insensitive": True
        }

        arg2payloadarg = {
            "title": "job_title_or",
            "description": "job_description_pattern_or",
            "location": "job_location_pattern_or",
            # NOTE: there is no available filter for job_type
            "salary_min": "min_salary_usd",
            "salary_max": "max_salary_usd",
            # NOTE: salary_currency is ignored because the only possibility to
            # search is with the keys above
            "company_name": "company_name_or",
            "required_skills": "company_technology_slug_or",
            "industry": "industry_or",
        }
        for arg, payloadarg in arg2payloadarg.items():
            value = query.get(arg, "")
            if not value:
                value = []
            if isinstance(value, str):
                if arg == "required_skills":
                    value = value.split(",")
                else:
                    value = [value, ]
            if value != []:
                payload[payloadarg] = value

        # make request
        print(f'Calling TheirStackAPI at {self.url} with payload: {payload}')
        THEIRSTACK_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbmFjc28xNzc3QGdtYWlsLmNvbSIsInBlcm1pc3Npb25zIjoidXNlciJ9.INiVTJLdZzzX0mp2lVNijE3sskdddli79dqluf9GEW0"
        headers = {
            "Authorization": f"Bearer {THEIRSTACK_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=100
        )

        jobs = []
        if response.status_code == 200:
            response_obj = response.json()
            for job in response_obj.get("data", []):
                # NOTE: concatenate location with hybrid and remote infos
                location = job.get("location", "")
                hybrid = job.get("hybrid", False)
                remote = job.get("remote", False)
                locations = []
                if location:
                    locations.append(location)
                if hybrid:
                    locations.append("Híbrido")
                if remote:
                    locations.append("Remoto")

                new_job = Job(
                    external_id=job["id"],
                    title=job.get("job_title", ""),
                    required_skills=job.get("company_object", {}).get("technology_names", []),
                    level=job.get("seniority", ""),
                    location=locations,
                    salary_min=job.get("min_annual_salary", None),
                    salary_max=job.get("max_annual_salary", None),
                    salary_currency=job.get("salary_currency", None),
                    description=job.get("description", ""),
                    job_type=[],  # NOTE: there is no easy way to get job_type
                    company_name=job.get("company_object", {}).get("name", ""),
                    published_date=job.get("date_posted", None),
                    url=job.get("url", ""),
                )
                jobs.append(new_job)

        return jobs
