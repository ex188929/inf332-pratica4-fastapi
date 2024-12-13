"""VagaGO API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vagago_api.routes import router

app = FastAPI(title="VagaGO API", version="0.0.1")

# Incluindo as rotas
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
