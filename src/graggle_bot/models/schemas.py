# src/graggle_bot/utils/models.py
from datetime import datetime

from pydantic import HttpUrl, TypeAdapter, field_validator
from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel

_http_url: TypeAdapter[HttpUrl] = TypeAdapter(HttpUrl)

class Website(SQLModel, table=True):
    url: str = Field(
        sa_column=Column(String(2048), primary_key=True)
    )
    status: int = Field(default=200, ge=100, le=599)
    last_change: datetime
    last_check: datetime
    announcement_channel: int

    up_embed_url: str = Field(
        sa_column=Column(String(2048))
    )
    down_embed_url: str = Field(
        sa_column=Column(String(2048))
    )

    @field_validator("url", "up_embed_url", "down_embed_url", mode="before")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return str(_http_url.validate_python(value))

class Option(SQLModel, table=True):
    name: str = Field(primary_key=True)
    enable: bool

class RCONServer(SQLModel, table=True):
    name: str = Field(primary_key=True)
    host: str
    port: int = Field(ge=1000, le=65535)
    password: str
