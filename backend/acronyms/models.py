"""Database models."""


import os
from typing import Iterator

import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


Base = declarative_base()


def get_db() -> Iterator[Session]:
    """Create engine and session for database."""
    type_ = os.environ.get("ACRONYMS_DATABASE_TYPE", "sqlite")
    database = os.environ.get("ACRONYMS_DATABASE_NAME", "acronyms")

    if type_ == "postgresql":
        host = os.environ["ACRONYMS_DATABASE_HOST"]
        password = os.environ["ACRONYMS_DATABASE_PASSWORD"]
        port = os.environ.get("ACRONYMS_DATABASE_PORT", "5432")
        user = os.environ["ACRONYMS_DATABASE_USER"]

        uri = f"{type_}://{user}:{password}@{host}:{port}/{database}"
        engine = sqlalchemy.create_engine(uri)
    elif type_ == "sqlite":
        uri = f"sqlite:///./{database}.db"
        engine = sqlalchemy.create_engine(
            uri, connect_args={"check_same_thread": False}
        )
    else:
        raise ValueError(f"Unsupported database type {type_}")

    Base.metadata.create_all(engine)
    with Session(engine) as session:  # type: ignore
        yield session


class Acronym(Base):
    """SQL model for acronyms table."""

    __tablename__ = "acronyms"
    __table_args__ = (UniqueConstraint("abbreviation", "phrase"),)
    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(String)
    phrase = Column(String)
