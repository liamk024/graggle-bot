from typing import List

from pydantic import HttpUrl
from sqlmodel import Session, select

from .database import engine
from .models import Option, Website


def get_all_websites() -> List[Website] | None:
    with Session(engine) as session:
        statement = select(Website)
        return list(session.exec(statement).all())
    return None

def get_option(option: str) -> Option | None:
    with Session(engine) as session:
        statement = select(Option).where(Option.name == option)
        results = session.exec(statement)
        saved_option: Option | None = results.first()
        return saved_option
    return None

def get_website(url: HttpUrl) -> Website | None:
    with Session(engine) as session:
        statement = select(Website).where(Website.url == url)
        results = session.exec(statement)
        user: Website | None = results.first()
        return user
    return None

def set_option(option: str, enable: bool) -> bool:
    with Session(engine) as session:
        existing: Option | None = session.get(Option, option)

        if existing is None:
            saved_option = Option(
                name=option,
                enable=enable,
            )
            session.add(saved_option)
        else:
            existing.enable = enable

        session.commit()
        return True
    return False

def set_website(website: Website) -> bool:
    with Session(engine) as session:
        existing: Website | None = session.get(Website, website.url)  # url is PK

        if existing is None:
            session.add(website)
        else:
            existing.status = website.status
            existing.last_change = website.last_change
            existing.last_check = website.last_check
            existing.announcement_channel = website.announcement_channel
            existing.up_embed_url = website.up_embed_url
            existing.down_embed_url = website.down_embed_url

        session.commit()
        return True
    return False

def delete_website(url: str) -> bool:
    with Session(engine) as session:
        exists: Website | None = session.exec(
            select(Website).where(Website.url == url)
        ).first()
        if not exists:
            return False

        session.delete(exists)
        session.commit()

        return True
    return False
