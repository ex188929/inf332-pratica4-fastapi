from setuptools import setup, find_packages

setup(
    name="vagago_api",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
    ],
    entry_points={
        "console_scripts": [
            "vagago-api=vagago_api.main:app",
        ],
    },
    author="INF332-Grupo01",
    description="An API based on FastAPI for VagaGO application.",
    python_requires=">=3.11",
)
