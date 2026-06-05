# src/graggle_bot/utils/database.py
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

from .models import Option, Website  # noqa: F401

engine: Engine = create_engine("sqlite:///database.db", echo=True)
SQLModel.metadata.create_all(engine)
