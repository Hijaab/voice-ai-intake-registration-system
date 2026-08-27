from sqlmodel import SQLModel, Session, create_engine
import os


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///patients.db")

# SQLite needs this option when used with Streamlit
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_db_and_tables():
    """
    Creates all SQLModel tables if they don't already exist.
    """

    SQLModel.metadata.create_all(engine)


# ============================================================
# DATABASE SESSION
# ============================================================

def get_session():
    """
    Returns a database session.
    """

    return Session(engine)