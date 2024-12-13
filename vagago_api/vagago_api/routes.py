"""Routes for VagaGO API."""

from itertools import zip_longest
from typing import List, Optional

from fastapi import APIRouter, Query, status
from sqlalchemy import text

from .models.Job import JobSchema
from .models.User import User, users_table, UserSchema
from .services.APIBRIntegration import APIBRIntegration
from .services.Database import Database
from .services.JobicyIntegration import JobicyIntegration
from .services.TheirStackIntegration import TheirStackIntegration

router = APIRouter()


@router.get("/jobs", summary="Vagas", tags=["Jobs"], response_model=List[JobSchema])
def get_jobs(
    title: Optional[str] = Query(None, description="Título da vaga"),
    required_skills: Optional[str] = Query(None, description="Habilidades requeridas"),
    location: Optional[str] = Query(None, description="Localização da vaga"),
    contracttype: Optional[str] = Query(None, description="Tipo de contrato"),
    salary_min: Optional[int] = Query(None, description="Salário mínimo"),
    salary_max: Optional[int] = Query(None, description="Salário máximo"),
    salary_currency: Optional[str] = Query(None, description="Moeda do salário"),
    description: Optional[str] = Query(None, description="Descrição da vaga"),
    company_name: Optional[str] = Query(None, description="Nome da empresa"),
    industry: Optional[str] = Query(None, description="Indústria"),
    count: Optional[int] = Query(10, description="Quantidade de vagas a retornar")
):
    """
    Retorna uma lista de vagas de emprego.
    """
    filters = {
        "title": title,
        "required_skills": required_skills,
        "location": location,
        "contracttype": contracttype,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "description": description,
        "company_name": company_name,
        "industry": industry,
        "count": count,
    }
    data = []

    # jobicy
    jobicy_integration = JobicyIntegration()
    jobicy_data = jobicy_integration.get_data(filters)
    jobicy_data = [job.to_dict() for job in jobicy_data]

    # APIBR
    apibr_integration = APIBRIntegration()
    apibr_data = apibr_integration.get_data(filters)
    apibr_data = [job.to_dict() for job in apibr_data]

    # TheirStack
    theirstack_integration = TheirStackIntegration()
    theirstack_data = theirstack_integration.get_data(filters)
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


@router.get(
    "/users/{user_id}",
    summary="Usuário",
    tags=["Users"],
    status_code=status.HTTP_200_OK,
)
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


@router.get(
    "/users",
    summary="Usuários",
    tags=["Users"],
    status_code=status.HTTP_200_OK,
)
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


@router.post(
    "/users",
    summary="Criar Usuário",
    tags=["Users"],
    status_code=status.HTTP_201_CREATED,
)
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


@router.put(
    "/users/{user_id}",
    summary="Atualizar Usuário",
    tags=["Users"],
    status_code=status.HTTP_200_OK
)
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


@router.delete(
    "/users/{user_id}",
    summary="Deletar Usuário",
    tags=["Users"],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(user_id: int):
    """
    Deleta um usuário.
    """
    db = Database()
    query = f"DELETE FROM users WHERE id = {user_id}"
    connection = db.get_connection()
    connection.execute(text(query))
    connection.commit()
