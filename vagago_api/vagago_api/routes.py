"""Routes for VagaGO API."""

from itertools import zip_longest
from typing import List, Optional

from fastapi import APIRouter, Query, Request, status
from sqlalchemy import text

from .models.User import User, users_table, UserSchema
from .services.APIBRIntegration import APIBRIntegration
from .services.Database import Database
from .services.JobicyIntegration import JobicyIntegration
from .services.TheirStackIntegration import TheirStackIntegration

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

    title = title_param if title_param else ""
    required_skills = required_skills_param if required_skills_param else ""
    location = location_param if location_param else ""
    contracttype = contracttype_param if contracttype_param else ""
    salarymin = salarymin_param if salarymin_param else ""
    salarymax = salarymax_param if salarymax_param else ""
    salarycurrency = salarycurrency_param if salarycurrency_param else ""
    description = description_param if description_param else ""
    companyname = companyname_param if companyname_param else ""
    industry = industry_param if industry_param else ""
    count = int(count_param) if count_param else 10  # to each API

    # jobicy
    jobicy_integration = JobicyIntegration()
    tags = []
    if required_skills:
        tags.append(required_skills)
    if title:
        tags.append(title)
    if description:
        tags.append(description)
    tag = ",".join(tags)
    jobicy_filters = {
        "count": count,  # Number of listings to return (default: 50, range: 1-50)
        "tag": tag,  # Search by job title and description (default: all jobs)
    }
    geo = jobicy_integration.validate_location(location) if location else "anywhere"
    if geo and geo != "anywhere":
        jobicy_filters["geo"] = geo
    bus = jobicy_integration.validate_business(industry) if industry else "all"
    if bus and bus != "all" and required_skills == "":
        jobicy_filters["industry"] = bus
    jobicy_data = jobicy_integration.get_data(jobicy_filters)
    jobicy_data = [job.to_dict() for job in jobicy_data]

    # APIBR
    apibr_integration = APIBRIntegration()
    terms = []
    if title:
        terms.append(title)
    if required_skills:
        # concatenate all filters, it uses blanks as separator
        terms.append(required_skills.replace(",", " "))
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
    theirstack_integration = TheirStackIntegration()
    theirstack_filters = {
        "count": count,
        "title": title,
        "description": description,
        "location": location,
        "salarymin": salarymin,
        "salarymax": salarymax,
        "salarycurrency": salarycurrency,
        "company_name": companyname,
        "required_skills": required_skills,
        "industry": industry,
    }
    theirstack_data = theirstack_integration.get_data(theirstack_filters)
    theirstack_data = [job.to_dict() for job in theirstack_data]

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


@router.get("/users/{user_id}", summary="Usuário", tags=["Users"], status_code=status.HTTP_200_OK)
def get_user(user_id: int):
    """
    Retorna um usuário por ID.
    """
    db = Database()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.query(query)

    (
        id,
        name,
        email,
        location,
        password,
        skills,
        _,
        desired_salary_min,
        desired_salary_max,
        desired_salary_currency,
    ) = result[0]

    user = User(
        id=id,
        name=name,
        email=email,
        location=location,
        password=password,
        skills=skills,
        desired_salary_min=desired_salary_min,
        desired_salary_max=desired_salary_max,
        desired_salary_currency=desired_salary_currency,
    )
    return user.to_dict()


@router.get("/users", summary="Usuários", tags=["Users"], status_code=status.HTTP_200_OK)
def get_users(
    name: Optional[str] = Query(None, description="Filtrar por nome (busca parcial)"),
    email: Optional[str] = Query(None, description="Filtrar por email (busca parcial)"),
    location: Optional[List[str]] = Query(None, description="Filtrar por localização"),
    skills: Optional[List[str]] = Query(None, description="Filtrar por habilidades"),
    desired_salary_min: Optional[float] = Query(None, description="Salário mínimo desejado"),
    desired_salary_max: Optional[float] = Query(None, description="Salário máximo desejado"),
    offset: int = Query(0, description="Número de registros para pular"),
    limit: int = Query(10, description="Número máximo de registros a retornar")
):
    """
    Retorna uma lista de usuários.
    """
    db = Database()

    query_parts = ["SELECT * FROM users"]
    params = {}
    where_conditions = []

    if name:
        where_conditions.append("name ILIKE :name")
        params['name'] = f"%{name}%"

    if email:
        where_conditions.append("email ILIKE :email")
        params['email'] = f"%{email}%"

    if location:
        where_conditions.append("location && :location")
        params['location'] = location

    if skills:
        where_conditions.append("skills && :skills")
        params['skills'] = skills

    if desired_salary_min is not None:
        where_conditions.append("desired_salary_min >= :desired_salary_min")
        params['desired_salary_min'] = desired_salary_min

    if desired_salary_max is not None:
        where_conditions.append("desired_salary_max <= :desired_salary_max")
        params['desired_salary_max'] = desired_salary_max

    if where_conditions:
        query_parts.append("WHERE " + " AND ".join(where_conditions))

    query_parts.append("OFFSET :offset LIMIT :limit")
    params['offset'] = offset
    params['limit'] = limit

    query = text(" ".join(query_parts))

    result = db.get_connection().execute(query, params)

    users = []
    for user in result:
        user_obj = User(
            id=user[0],
            name=user[1],
            email=user[2],
            location=user[3],
            password=user[4],
            skills=user[5],
            desired_salary_min=user[7],
            desired_salary_max=user[8],
            desired_salary_currency=user[9],
        )
        users.append(user_obj.to_dict())

    return users


@router.post("/users", summary="Criar Usuário", tags=["Users"], status_code=status.HTTP_201_CREATED)
def create_user(user: UserSchema):
    """
    Cria um usuário.
    """
    db = Database()

    values = {
        'name': user.name,
        'email': user.email,
        'location': user.location,
        'password': user.password,
        'skills': user.skills,
        'desired_salary_min': user.desired_salary_min,
        'desired_salary_max': user.desired_salary_max,
        'desired_salary_currency': user.desired_salary_currency
    }

    result = db.insert(users_table, values)  # 'users' deve ser a tabela SQLAlchemy correspondente

    userResponse = User(
        id=result[0],
        name=result[1],
        email=result[2],
        location=result[3],
        password=result[4],
        skills=result[5],
        desired_salary_min=result[6],
        desired_salary_max=result[7],
        desired_salary_currency=result[8],
    )
    return userResponse.to_dict()

@router.put("/users/{user_id}", summary="Atualizar Usuário", tags=["Users"], status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UserSchema):
    """
    Atualiza um usuário.
    """
    db = Database()

    update_fields = {
        k: v for k, v in {
            'name': user.name,
            'email': user.email,
            'location': user.location,
            'password': user.password,
            'skills': user.skills,
            'desired_salary_min': user.desired_salary_min,
            'desired_salary_max': user.desired_salary_max,
            'desired_salary_currency': user.desired_salary_currency
        }.items() if v is not None
    }

    set_clauses = []
    params = {"user_id": user_id}
    for key, value in update_fields.items():
        set_clauses.append(f"{key} = :{key}")
        params[key] = value

    query = text(f"""
        UPDATE users
        SET {', '.join(set_clauses)}
        WHERE id = :user_id
    """)

    connection = db.get_connection()
    connection.execute(query, params)
    connection.commit()

@router.delete("/users/{user_id}", summary="Deletar Usuário", tags=["Users"], status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """
    Deleta um usuário.
    """
    db = Database()
    query = f"DELETE FROM users WHERE id = {user_id}"
    connection = db.get_connection()
    connection.execute(text(query))
    connection.commit()
