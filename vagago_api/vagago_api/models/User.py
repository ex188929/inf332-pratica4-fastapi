import uuid


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
