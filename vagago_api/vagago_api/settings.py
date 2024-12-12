from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "VagaGO API"
    environment: str = "development"
    THEIRSTACK_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJleDE4ODkzMkBnLnVuaWNhbXAuYnIiLCJwZXJtaXNzaW9ucyI6InVzZXIifQ.uD9MuJCpzOU18cUDmDS_TXncuzolXvmNV6wDt5q6boA"

settings = Settings()