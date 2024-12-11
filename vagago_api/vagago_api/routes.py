from fastapi import APIRouter, Request
from .services.JobicyIntegration import JobicyIntegration
from .services.Database import Database
from .models.User import User
from .services.APIBRIntegration import APIBRIntegration

router = APIRouter()


@router.get("/jobs", summary="Vagas", tags=["Jobs"])
def get_jobs(request: Request):
    """
    Retorna uma lista de vagas de emprego.
    """
    data = []

    # TODO: parse filters to each API
    count = 10
    filters = "fullstack"  # TODO: must be used to build tag (Jobicy) and term (APIBR)

    # get all query parameters
    location_param = request.query_params.get("location")

    # jobicy
    jobicy_integration = JobicyIntegration()
    geo = jobicy_integration.validate_location(location_param) if location_param else []
    jobicy_data = jobicy_integration.get_data(
        {
            "count": count,  # Number of listings to return (default: 50, range: 1-50)
            "geo": geo if geo else "brazil",  # Filter by country (default: brazil)
            "industry": "dev",  # Filter by job category (default: all categories)
            # NOTE: it doesn't return anything for any tag I try to use, it seems to be a bug...
            # "tag": filters,  # Search by job title and description (default: all jobs)
        }
    )
    jobicy_data = [job.to_dict() for job in jobicy_data]

    # APIBR
    # TODO: concatenate all filters? it seems to use comma separator
    term = ",".join(filters)
    term += ",Brasil"

    apibr_integration = APIBRIntegration()
    apibr_data = apibr_integration.get_data(
        {
            "page": 1,  # page number
            "per_page": count,  # number of listings to return
            # "term": term,
        }
    )
    apibr_data = [job.to_dict() for job in apibr_data]

    # TheirStack
    # TODO

    # TODO: pagination
    data.extend(jobicy_data)
    data.extend(apibr_data)

    return data


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
