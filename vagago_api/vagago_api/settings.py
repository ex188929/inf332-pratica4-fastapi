from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "VagaGO API"
    environment: str = "development"


settings = Settings()
