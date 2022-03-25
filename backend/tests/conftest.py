"""Resuable testing fixtures for acronyms."""


from typing import Iterator

from fastapi.testclient import TestClient
from psycopg2.extensions import connection as Connection
import pytest
import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from acronyms.__main__ import app
from acronyms.models import Acronym, Base, get_db


@pytest.fixture
def client(database: Session) -> TestClient:
    """Fast API test client."""
    app.dependency_overrides[get_db] = lambda: database
    return TestClient(app)


@pytest.fixture
def connection(postgresql: Connection) -> str:
    """Connection URI for temporary PostgreSQL database."""
    user = postgresql.info.user
    address = f"{postgresql.info.host}:{postgresql.info.port}"
    name = postgresql.info.dbname
    return f"postgresql://{user}:@{address}/{name}"


@pytest.fixture
def database(session: Session) -> Session:
    """Connection URI for temporary PostgreSQL database."""
    acronyms = [
        Acronym(abbreviation="AM", expansion="Ante Meridiem"),
        Acronym(abbreviation="DM", expansion="Data Mining"),
        Acronym(abbreviation="DM", expansion="Direct Message"),
        Acronym(abbreviation="RIP", expansion="Rest In Peace"),
        Acronym(abbreviation="JSON", expansion="JavaScript Object Notation"),
    ]

    for acronym in acronyms:
        session.add(acronym)
    session.commit()
    return session


@pytest.fixture
def engine(connection: Connection) -> Engine:
    """Engine for temporary PostgreSQL database."""
    return sqlalchemy.create_engine(connection)


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Session for temporary PostgreSQL database."""
    Base.metadata.create_all(engine)
    # Mypy claims Session has no attribute __enter__, which is incorrect as
    # shown at
    # https://github.com/sqlalchemy/sqlalchemy/blob/52e8545b2df312898d46f6a5b119675e8d0aa956/lib/sqlalchemy/orm/session.py#L1156.
    with Session(engine) as session:  # type: ignore
        yield session
