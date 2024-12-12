"""Routes for VagaGO API."""

from itertools import zip_longest

from fastapi import APIRouter, Request

from .models.User import User
from .services.APIBRIntegration import APIBRIntegration
from .services.Database import Database
from .services.JobicyIntegration import JobicyIntegration

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

    count = int(count_param) if count_param else 10  # to each API

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
    apibr_integration = APIBRIntegration()
    # concatenate all filters, it uses blanks as separator
    title = title_param if title_param else ""
    required_skills = " ".join(required_skills_param.split(',')) if required_skills_param else ""
    location = location_param if location_param else ""
    contracttype = contracttype_param if contracttype_param else ""
    companyname = companyname_param if companyname_param else ""
    terms = []
    if title:
        terms.append(title)
    if required_skills:
        terms.append(required_skills)
    if location:
        terms.append(location)
    if contracttype:
        terms.append(contracttype)
    if companyname:
        terms.append(companyname)
    term = " ".join(terms)
    apibr_filters = {
        "page": 1,  # page number
        "per_page": count,  # number of listings to return
        "term": term,
    }
    apibr_data = apibr_integration.get_data(apibr_filters)
    apibr_data = [job.to_dict() for job in apibr_data]

    # TheirStack
    # TODO
    theirstack_data = []

    # Pagination
    data = [
        item
        for triplet in zip_longest(jobicy_data, apibr_data, theirstack_data)
        for item in triplet
        if item is not None
    ]
    if len(data) > count:
        data = data[:count]
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
