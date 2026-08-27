import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine


# Load environment variables from .env
load_dotenv()


# ---------------------------------------------------------
# DATABASE URL
# ---------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./patients.db",
)


# ---------------------------------------------------------
# SQLITE CONFIGURATION
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# ---------------------------------------------------------
# DATABASE ENGINE
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


# ---------------------------------------------------------
# CREATE TABLES
# ---------------------------------------------------------

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------
# DATABASE SESSION
# ---------------------------------------------------------

def get_session():
    return Session(engine)