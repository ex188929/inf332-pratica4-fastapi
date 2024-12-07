"""VagaGO API."""

from fastapi import FastAPI
from vagago_api.routes import router

app = FastAPI(title="Hello World API", version="1.0.0")

# Incluindo as rotas
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
