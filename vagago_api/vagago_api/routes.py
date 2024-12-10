from fastapi import APIRouter
from .services.JobicyIntegration import JobicyIntegration
from .services.Database import Database
from .models.User import User

router = APIRouter()


@router.get("/jobs", summary="Vagas", tags=["Jobs"])
def get_jobs():
    """
    Retorna uma lista de vagas de emprego.
    """
    jobicy_integration = JobicyIntegration()
    jobicy_data = jobicy_integration.get_data({"geo": "brazil", "industry": "dev", "count": 5})
    jobicy_data = [job.to_dict() for job in jobicy_data]
    return jobicy_data

@router.get("/users/{user_id}", summary="Usuário", tags=["Users"])
def get_user(user_id: int):
    """
    Retorna um usuário por ID.
    """
    db = Database()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.query(query)
    print(result)
    user = User(
        id=result[0],
        name=result[1],
        email=result[2],
        location=result[3],
        password=result[4],
        skills=result[5],
        desired_salary_min=result[7],
        desired_salary_max=result[8],
        desired_salary_currency=result[9],
    )
    return user.to_dict()