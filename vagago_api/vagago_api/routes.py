from fastapi import APIRouter, Request
from .services.JobicyIntegration import JobicyIntegration
from .services.Database import Database
from .models.User import User
from .services.APIBRIntegration import APIBRIntegration
from .services.TheirStackIntegration import TheirStackIntegration

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
    industry_param = request.query_params.get("industry")
    required_skills_param = request.query_params.get("required_skills")
    title_param = request.query_params.get("title")
    description_param = request.query_params.get("description")
    contract_type_param = request.query_params.get("contract_type")
    experience_level_param = request.query_params.get("experience_level")
    published_date_param = request.query_params.get("published_date")
    job_type_param = request.query_params.get("job_type")
    employer_id_param = request.query_params.get("employer_id")
    salary_range_param = request.query_params.get("salary_range")
    languages_param = request.query_params.get("languages")
    education_level_param = request.query_params.get("education_level")

    # jobicy

    jobicy_integration = JobicyIntegration()
    geo = jobicy_integration.validate_location(location_param) if location_param else "anywhere"
    industry = jobicy_integration.validate_business(industry_param) if industry_param else "all"
    required_skills = required_skills_param if required_skills_param else ""
    title = title_param if title_param else ""
    description = description_param if description_param else ""
    jobicy_filters = {
        "count": count,  # Number of listings to return (default: 50, range: 1-50)
        "tag": required_skills + "," + title + ',' + description,  # Search by job title and description (default: all jobs)
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
    theirstack_integration = TheirStackIntegration()
    theirstack_data = theirstack_integration.get_data(
        {
            "count": count,  # Number of listings to return
            "term": filters,  # Search term
            "location": location_param,  # Location filter
            "contract_type": contract_type_param,
            "experience_level": experience_level_param,
            "published_date": published_date_param,
            "job_type": job_type_param,
            "skills": required_skills_param.split(",") if required_skills_param else [],
            "industries": industry_param.split(",") if industry_param else [],
            "employer_id": employer_id_param,
            "salary_range": salary_range_param,
            "languages": languages_param.split(",") if languages_param else [],
            "education_level": education_level_param
        }
    )
    theirstack_data = [job.to_dict() for job in theirstack_data]

    # TODO: pagination
    data.extend(jobicy_data)
    data.extend(apibr_data)
    data.extend(theirstack_data)

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