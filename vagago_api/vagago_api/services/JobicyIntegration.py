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

valid_business = [
    "business",
    "copywriting",
    "supporting",
    "data-science",
    "design-multimedia",
    "admin",
    "accounting-finance",
    "hr",
    "marketing",
    "management",
    "dev",
    "seller",
    "seo",
    "smm",
    "engineering",
    "technical-support",
    "web-app-design",
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
        return "anywhere"

    def validate_business(self, business_query: str) -> str:
        print(
            "Jobicy only accepts one parameter for business, so we will return the first valid business found."
        )
        for bus in business_query.split(","):
            if bus in valid_business:
                return bus
        return "all"

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
        title = query.get("title", "")
        required_skills = query.get("required_skills", "")
        location = query.get("location", "")
        contracttype = query.get("contracttype", "")  # not used
        salary_min = query.get("salary_min", None)  # not used
        salary_max = query.get("salary_max", None)  # not used
        salary_currency = query.get("salary_currency", "")  # not used
        description = query.get("description", "")
        company_name = query.get("company_name", "")  # not used
        industry = query.get("industry", "")
        count = query.get("count", 10)

        # parse params
        params = {
            "count": count,  # Number of listings to return (default: 50, range: 1-50)
        }
        tags = []
        if required_skills:
            tags.append(required_skills)
        if title:
            tags.append(title)
        if description:
            tags.append(description)
        tag = ",".join(tags)
        if tag:
            params["tag"] = tag  # Search by job title and description (default: all jobs)

        geo = self.validate_location(location) if location else "anywhere"
        if geo and geo != "anywhere":
            params["geo"] = geo

        bus = self.validate_business(industry) if industry else "all"
        if bus and bus != "all" and tag == "":
            params["industry"] = bus

        # make request
        print("Calling Jobicy API at ", self.url, " with query ", params)
        response = requests.get(self.url, params=params, timeout=100)
        response_obj = response.json()
        jobs = []

        # handle empty responses
        iserror = isinstance(response_obj["jobs"], dict)
        if iserror:
            return jobs

        # parse response for status code 200
        for job in response_obj["jobs"]:
            jobgeo = job.get("jobGeo", [])
            if isinstance(jobgeo, str):
                jobgeo = [jobgeo, ]
            jobtype = job.get("jobType", [])
            if isinstance(jobtype, str):
                jobtype = [jobtype, ]

            new_job = Job(
                external_id=job["id"],
                title=job.get("jobTitle", ""),
                required_skills=[],  # TODO: parse description with LLM
                level=job.get("jobLevel", ""),
                location=jobgeo,
                salary_min=job.get("annualSalaryMin", None),
                salary_max=job.get("annualSalaryMax", None),
                salary_currency=job.get("salaryCurrency", None),
                description=job.get("jobDescription", ""),
                job_type=jobtype,
                company_name=job.get("companyName", ""),
                published_date=job.get("pubDate", None),
                url=job.get("url", ""),
            )
            jobs.append(new_job)

        return jobs
