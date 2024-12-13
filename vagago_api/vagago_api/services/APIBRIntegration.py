import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job


class APIBRIntegration(APIIntegration):
    def __init__(self):
        super().__init__("APIBR", "https://apibr.com/vagas/api/v2/issues")

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
        contracttype = query.get("contracttype", "")
        salary_min = query.get("salary_min", None)
        salary_max = query.get("salary_max", None)
        salary_currency = query.get("salary_currency", "")
        description = query.get("description", "")
        company_name = query.get("company_name", "")
        industry = query.get("industry", "")  # not used
        count = query.get("count", 10)

        # parse params
        params = {
            "page": 1,
            "per_page": count,
        }
        terms = []
        if title:
            terms.append(title)
        if required_skills:
            # concatenate all filters, it uses blanks as separator
            terms.append(required_skills.replace(",", " "))
        if location:
            terms.append(location)
        if contracttype:
            terms.append(contracttype)
        if company_name:
            terms.append(company_name)
        term = " ".join(terms)
        if term:
            params["term"] = term

        # make request
        print(f"Calling APIBR at {self.url} with params: {params}")
        headers = {
            "accept": "application/json",
            # after several hours of debug, I found that this header is necessary
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
        for job in response_obj:
            # parse labels
            labels = job["labels"]
            skills, levels, locations, job_type = [], [], [], []
            for lab in labels:
                # NOTE: this is an attempt to parse labels, there is no
                # pattern to help us
                lname, ltype, lcolor = lab["name"], lab["type"], lab["color"]
                if lname in [
                        "Estágio", "Estagiário", "Júnior", "Pleno",
                        "Sênior", "Especialista",
                        ]:
                    levels.append(lname)
                elif lname in ["CLT", "Contrato", "Freelance", "PJ"]:
                    job_type.append(lname)
                elif lname in [
                        "Híbrido", "Presencial", "Remoto", "Semi-presencial",
                        ]:
                    locations.append(lname)
                elif ltype == "APIBr":
                    # NOTE: there is no easy way to differentiate skills and
                    # locations
                    if lname in [
                            "Backend", "Frontend", "Mobile", "Android", "Qa"
                            ]:
                        skills.append(lname)
                    else:
                        locations.append(lname)
                elif ltype == "label":
                    # NOTE: there is no easy way to differentiate skills and
                    # locations. I noticed that in some cases the separator is
                    # used to indicate states or countries, and in some
                    # repos the black color is used for several locations.
                    # There is no garantee this is correct...
                    if " - " in lname or "/" in lname or lcolor == "000000":
                        locations.append(lname)
                    else:
                        skills.append(lname)

            # NOTE: decided to concatenate levels because the default value is
            # a string
            level = "/".join(levels)
            # NOTE: there is no easy way to get salary
            salary_min, salary_max, salary_currency = None, None, None
            # NOTE: there is not easy way to get the full description
            description = ""
            # NOTE: decided to consider the author of the issue as the company
            company_name = job["user"]["login"]

            new_job = Job(
                external_id=job["id"],
                title=job.get("title", ""),
                required_skills=skills,
                level=level,
                location=locations,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency=salary_currency,
                description=description,
                job_type=job_type,
                company_name=company_name,
                published_date=job["created_at"],
                url=job.get("url", ""),
            )
            jobs.append(new_job)

        return jobs
