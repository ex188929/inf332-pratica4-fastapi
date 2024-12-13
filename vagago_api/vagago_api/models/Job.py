import uuid
from typing import List, Optional

from pydantic import BaseModel


class Job:
    def __init__(
        self,
        external_id,
        title="",
        required_skills=[],
        level="",
        location=[],
        salary_min=None,
        salary_max=None,
        salary_currency=None,
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
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary_currency = salary_currency
        self.description = description
        self.job_type = job_type
        self.company_name = company_name
        self.published_date = published_date
        self.url = url

    def __repr__(self):
        return f'<Job {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "required_skills": self.required_skills,
            "level": self.level,
            "location": self.location,
            "description": self.description,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "job_type": self.job_type,
            "company_name": self.company_name,
            "published_date": self.published_date,
            "url": self.url,
        }


class JobSchema(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    required_skills: Optional[List[str]] = None
    level: Optional[str] = None
    location: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    description: Optional[str] = None
    job_type: Optional[List[str]] = None
    company_name: Optional[str] = None
    published_date: Optional[str] = None  # ISO 8601 string format
    url: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "required_skills": self.required_skills,
            "level": self.level,
            "location": self.location,
            "description": self.description,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "job_type": self.job_type,
            "company_name": self.company_name,
            "published_date": self.published_date,
            "url": self.url,
        }
