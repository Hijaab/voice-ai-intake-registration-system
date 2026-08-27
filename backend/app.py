import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables
from .routes.patients import router as patients_router
from .routes.voice import router as voice_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


app = FastAPI(
    title="Voice AI Patient Registration API",
    description=(
        "REST API for the Voice AI Patient Registration "
        "System."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():

    create_db_and_tables()

    logging.info(
        "Database initialized successfully."
    )


@app.get("/")
def root():

    return {
        "data": {
            "service": "Voice AI Patient Registration API",
            "status": "online",
        },
        "error": None,
    }


@app.get("/health")
def health():

    return {
        "data": {
            "status": "healthy"
        },
        "error": None,
    }


app.include_router(
    patients_router
)

app.include_router(
    voice_router
)