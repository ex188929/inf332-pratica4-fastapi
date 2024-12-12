from typing import List, Optional
from sqlalchemy import text
from fastapi import APIRouter, Request, status, Query
from .services.JobicyIntegration import JobicyIntegration
from .services.Database import Database
from .models.User import User, UserSchema, users_table
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
    industry_param = request.query_params.get("industry")
    required_skills_param = request.query_params.get("required_skills")
    title_param = request.query_params.get("title")
    description_param = request.query_params.get("description")

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
    # TODO

    # TODO: pagination
    data.extend(jobicy_data)
    data.extend(apibr_data)

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
