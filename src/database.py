# src/database.py
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

from src.models.schemas import Option, Website  # noqa: F401
from src.utils.config import DB_LOCATION

engine: Engine = create_engine(DB_LOCATION)
SQLModel.metadata.create_all(engine)
