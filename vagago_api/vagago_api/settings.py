from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Hello World API"
    environment: str = "development"


settings = Settings()
