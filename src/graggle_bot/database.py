# src/graggle_bot/utils/database.py
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

from graggle_bot.models.schemas import Option, Website  # noqa: F401
from graggle_bot.utils.config import DB_LOCATION

engine: Engine = create_engine(DB_LOCATION)
SQLModel.metadata.create_all(engine)
