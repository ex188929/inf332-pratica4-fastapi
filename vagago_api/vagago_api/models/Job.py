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
        salary_currency=None,
        description="",
        job_type=[],
        company_name="",
        published_date=None,
        url="",
        education_level="",
        languages=[],
        salary_range=None
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
        self.salary_currency = salary_currency
        self.description = description
        self.job_type = job_type
        self.company_name = company_name
        self.published_date = published_date
        self.url = url
        self.education_level = education_level
        self.languages = languages
        self.salary_range = salary_range

    def __repr__(self):
        return f'<Job {self.id}>'

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
            "salary_currency": self.salary_currency,
            "job_type": self.job_type,
            "company_name": self.company_name,
            "published_date": self.published_date,
            "url": self.url,
            "education_level": self.education_level,
            "languages": self.languages,
            "salary_range": self.salary_range,
        }
