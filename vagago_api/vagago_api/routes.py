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

    # get all query parameters
    title_param = request.query_params.get("title")
    required_skills_param = request.query_params.get("required_skills")
    location_param = request.query_params.get("location")
    contracttype_param = request.query_params.get("contracttype")
    salarymin_param = request.query_params.get("salary_min")
    salarymax_param = request.query_params.get("salary_max")
    salarycurrency_param = request.query_params.get("salary_currency")
    description_param = request.query_params.get("description")
    companyname_param = request.query_params.get("companyname")
    industry_param = request.query_params.get("industry")
    count_param = request.query_params.get("count")

    count = count_param if count_param else 10  # to each API

    # jobicy
    jobicy_integration = JobicyIntegration()
    geo = jobicy_integration.validate_location(location_param) if location_param else "anywhere"
    industry = jobicy_integration.validate_business(industry_param) if industry_param else "all"
    required_skills = required_skills_param if required_skills_param else ""
    title = title_param if title_param else ""
    description = description_param if description_param else ""
    tags = []
    if required_skills:
        tags.append(required_skills)
    if title:
        tags.append(description)
    if description:
        tags.append(description)
    tag = ",".join(tags)
    jobicy_filters = {
        "count": count,  # Number of listings to return (default: 50, range: 1-50)
        "tag": tag,  # Search by job title and description (default: all jobs)
    }
    if geo and geo != "anywhere":
        jobicy_filters["geo"] = geo
    if industry and industry != "all" and required_skills == "":
        jobicy_filters["industry"] = industry
    jobicy_data = jobicy_integration.get_data(jobicy_filters)
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
