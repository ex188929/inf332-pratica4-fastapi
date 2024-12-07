from fastapi import APIRouter

router = APIRouter()


@router.get("/hello", summary="Say Hello", tags=["Hello"])
def say_hello():
    """
    Route for hello world.
    """
    return {"message": "Hello, World!"}
