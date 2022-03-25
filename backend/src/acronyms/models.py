"""Database models."""


import os
from typing import Iterator

import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


Base = declarative_base()


def get_db() -> Iterator[Session]:
    """Engine and session for PostgreSQL database."""
    database = os.environ["ACRONYMS_POSTGRES_DB"]
    host = os.environ["ACRONYMS_POSTGRES_HOST"]
    password = os.environ["ACRONYMS_POSTGRES_PASSWORD"]
    port = os.environ["ACRONYMS_POSTGRES_PORT"]
    user = os.environ["ACRONYMS_POSTGRES_USER"]
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    engine = sqlalchemy.create_engine(database_url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:  # type: ignore
        yield session


class Acronym(Base):
    """SQL model for acronyms table."""

    __tablename__ = "acronyms"
    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(String)
    expansion = Column(String)
