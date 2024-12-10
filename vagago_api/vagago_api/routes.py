from fastapi import APIRouter
from .services.JobicyIntegration import JobicyIntegration

router = APIRouter()


@router.get("/jobs", summary="Vagas", tags=["Jobs"])
def say_hello():
    """
    Retorna uma lista de vagas de emprego.
    """
    jobicy_integration = JobicyIntegration()
    jobicy_data = jobicy_integration.get_data({"geo": "brazil", "industry": "dev"})
    jobicy_data = [job.to_dict() for job in jobicy_data]
    return jobicy_data
