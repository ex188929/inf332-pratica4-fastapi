import requests
from .APIIntegration import APIIntegration
from ..models.Job import Job
from vivago_api.settings import THEIRSTACK_API_KEY

class TheirStackIntegration(APIIntegration):
    def __init__(self):
        super().__init__("TheirStack", "https://api.theirstack.com/v1/jobs/search")

    def get_data(self, query: dict) -> list[Job]:
        # Mapeamento dos filtros aceitos pela API TheirStack
        params = {
            "term": query.get("term", ""),  # Termo de busca
            "location": query.get("location", ""),  # Localização
            "contract_type": query.get("contract_type", ""),  # Tipo de contrato
            "experience_level": query.get("experience_level", ""),  # Nível de experiência
            "published_date": query.get("published_date", ""),  # Data de publicação
            "job_type": query.get("job_type", ""),  # Tipo de vaga
            "skills": query.get("skills", []),  # Habilidades requeridas
            "industries": query.get("industries", []),  # Indústrias ou áreas de negócio
            "count": query.get("count", 10),  # Número de vagas a retornar
            "employer_id": query.get("employer_id", ""),  # Empregador específico
            "salary_range": query.get("salary_range", ""),  # Faixa salarial
            "keywords": query.get("keywords", ""),  # Palavras-chave adicionais
            "availability": query.get("availability", ""),  # Disponibilidade da vaga
            "languages": query.get("languages", []),  # Idiomas exigidos
            "education_level": query.get("education_level", "")  # Nível de educação
        }

        # Remover parâmetros vazios ou não configurados
        params = {k: v for k, v in params.items() if v}

        # Configuração dos headers para autenticação e formato de resposta
        headers = {
            "Authorization": f"Bearer {THEIRSTACK_API_KEY}",
            "accept": "application/json"
        }

        # Requisição POST à API TheirStack
        response = requests.post(
            self.url,
            json=params,
            headers=headers,
            timeout=100,
        )

        # Verificação do status da resposta
        if response.status_code == 200:
            response_obj = response.json()
            jobs = []

            # Processamento das vagas retornadas
            for job in response_obj.get("jobs", []):
                new_job = Job(
                    external_id=job.get("id", ""),
                    title=job.get("title", ""),
                    required_skills=job.get("skills", []),
                    level=job.get("experience_level", ""),
                    location=job.get("location", ""),
                    salary_min=job.get("salary_min", None),
                    salary_max=job.get("salary_max", None),
                    salary_currency=job.get("salary_currency", ""),
                    description=job.get("description", ""),
                    job_type=job.get("job_type", []),
                    company_name=job.get("company_name", ""),
                    published_date=job.get("published_date", None),
                    url=job.get("url", "")
                )
                jobs.append(new_job)
            return jobs
        else:
            response.raise_for_status()