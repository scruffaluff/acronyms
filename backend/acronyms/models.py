"""Database models."""


import os
from typing import Iterator, Literal

import sqlalchemy
from sqlalchemy import (
    CheckConstraint,
    Column,
    Integer,
    Unicode,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


Base = declarative_base()


class Acronym(Base):
    """SQL model for acronyms table."""

    __tablename__ = "acronyms"
    __table_args__ = (UniqueConstraint("abbreviation", "phrase"),)
    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(
        Unicode,
        CheckConstraint("LENGTH(abbreviation) > 0"),
        index=True,
        nullable=False,
    )
    description = Column(Unicode, nullable=True)
    phrase = Column(
        Unicode,
        CheckConstraint("LENGTH(phrase) > 0"),
        index=True,
        nullable=False,
    )


# TODO: Figure out to directly infer type of all column names for Acronym.
AcronymColumn = Literal["id", "abbreviation", "phrase"]


def db_uri() -> str:
    """Create engine and session for database."""
    type_ = os.environ.get("ACRONYMS_DATABASE_TYPE", "sqlite")
    database = os.environ.get("ACRONYMS_DATABASE_NAME", "acronyms")

    if type_ == "postgresql":
        host = os.environ["ACRONYMS_DATABASE_HOST"]
        password = os.environ["ACRONYMS_DATABASE_PASSWORD"]
        port = os.environ.get("ACRONYMS_DATABASE_PORT", "5432")
        user = os.environ["ACRONYMS_DATABASE_USER"]

        return f"{type_}://{user}:{password}@{host}:{port}/{database}"
    elif type_ == "sqlite":
        return f"sqlite:///./{database}.db"
    else:
        raise ValueError(f"Unsupported database type {type_}")


def get_db() -> Iterator[Session]:
    """Create engine and session for database."""
    uri = db_uri()
    type_ = uri.split("://")[0]

    if type_ == "sqlite":
        engine = sqlalchemy.create_engine(
            uri, connect_args={"check_same_thread": False}
        )
    else:
        engine = sqlalchemy.create_engine(uri)

    Base.metadata.create_all(engine)
    # Typing disabled since Mypy falsely believes that Session is not a context
    # manager.
    with Session(engine) as session:  # type: ignore
        yield session
