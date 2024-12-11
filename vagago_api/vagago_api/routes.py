from fastapi import APIRouter
from .services.JobicyIntegration import JobicyIntegration
from .services.APIBRIntegration import APIBRIntegration
from .services.TheirStackIntegration import TheirStackIntegration

router = APIRouter()

@router.get("/jobs", summary="Vagas", tags=["Jobs"])
def say_hello():  # TODO: add args
    """
    Retorna uma lista de vagas de emprego.
    """
    data = []

    # TODO: parse filters to each API
    count = 10
    filters = "fullstack"  # TODO: must be used to build tag (Jobicy) and term (APIBR)

    # Jobicy
    jobicy_integration = JobicyIntegration()
    jobicy_data = jobicy_integration.get_data(
        {
            "count": count,  # Number of listings to return (default: 50, range: 1-50)
            "geo": "brazil",  # Filter by job region (default: all regions)
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
    theirstack_integration = TheirStackIntegration()
    theirstack_data = theirstack_integration.get_data(
        {
            "count": count,  # Number of listings to return
            "term": filters,  # Search term
            "location": "Brazil"  # Location filter
        }
    )
    theirstack_data = [job.to_dict() for job in theirstack_data]

    # TODO: pagination
    data.extend(jobicy_data)
    data.extend(apibr_data)
    data.extend(theirstack_data)

    return data