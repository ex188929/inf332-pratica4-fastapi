import uuid
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import Table, Column, Integer, String, ARRAY, MetaData

metadata = MetaData()

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('email', String, nullable=False),
    Column('location', ARRAY(String), nullable=False),
    Column('password', String, nullable=False),
    Column('skills', ARRAY(String)),
    Column('desired_salary_min', Integer),
    Column('desired_salary_max', Integer),
    Column('desired_salary_currency', String)
)

class User:
    def __init__(
        self,
        id,
        name,
        email,
        password="",
        location=None,
        skills=None,
        desired_salary_min=None,
        desired_salary_max=None,
        desired_salary_currency="",
    ):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.email = email
        self.location = location if location is not None else []
        # TODO transform password in hash
        self.password = password
        self.skills = skills if skills is not None else []
        self.desired_salary_min = desired_salary_min
        self.desired_salary_max = desired_salary_max
        self.desired_salary_currency = desired_salary_currency

    def __repr__(self):
        return f"<User {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "location": self.location,
            "skills": self.skills,
            "desired_salary_min": self.desired_salary_min,
            "desired_salary_max": self.desired_salary_max,
            "desired_salary_currency": self.desired_salary_currency,
        }

class UserSchema(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[List[str]] = None
    password: Optional[str] = None
    skills: Optional[List[str]] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    desired_salary_currency: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id or str(uuid.uuid4()),
            "name": self.name,
            "email": self.email,
            "location": self.location,
            "skills": self.skills,
            "desired_salary_min": self.desired_salary_min,
            "desired_salary_max": self.desired_salary_max,
            "desired_salary_currency": self.desired_salary_currency,
        }
