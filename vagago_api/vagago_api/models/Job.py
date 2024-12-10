import uuid


class Job:
    def __init__(
        self,
        external_id,
        title="",
        required_skills=[],
        level="",
        location=[],
        contract_type="",
        salary_min=None,
        salary_max=None,
        description="",
        job_type=[],
        company_name="",
        published_date=None,
        url="",
    ):
        self.id = str(uuid.uuid4())
        self.external_id = external_id
        self.title = title
        self.required_skills = required_skills
        self.level = level
        self.location = location
        self.contract_type = contract_type
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.description = description
        self.job_type = job_type
        self.company_name = company_name
        self.published_date = published_date
        self.url = url

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "required_skills": self.required_skills,
            "level": self.level,
            "location": self.location,
            "contract_type": self.contract_type,
            "description": self.description,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "job_type": self.job_type,
            "company_name": self.company_name,
            "published_date": self.published_date,
            "url": self.url,
        }
