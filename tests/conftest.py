"""Resuable testing fixtures for acronyms."""


import subprocess
from subprocess import Popen
from typing import Iterator

from fastapi.testclient import TestClient
from psycopg import Connection
import pytest
import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from acronyms.models import Acronym, Base, get_db


@pytest.fixture
def client(database: Session) -> TestClient:
    """Fast API test client."""
    # App import placed here since it depends on prebuilt Node assets, which are
    # not required for end to end tests.
    from acronyms.site import app

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
        Acronym(abbreviation="AM", phrase="Ante Meridiem"),
        Acronym(abbreviation="DM", phrase="Data Mining"),
        Acronym(abbreviation="DM", phrase="Direct Message"),
        Acronym(abbreviation="RIP", phrase="Rest In Peace"),
        Acronym(abbreviation="JSON", phrase="JavaScript Object Notation"),
    ]

    for acronym in acronyms:
        session.add(acronym)
    session.commit()
    return session


@pytest.fixture
def engine(connection: str) -> Engine:
    """Engine for temporary PostgreSQL database."""
    return sqlalchemy.create_engine(connection)


@pytest.fixture(scope="session")
def server() -> Iterator[str]:
    """Compile frontend assets and starts backend server."""
    # Running the server via uvicorn directly as a Python function throws
    # "RuntimeError: asyncio.run() cannot be called from a running event loop".
    process = Popen(
        ["acronyms", "--port", "8081"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    yield "http://localhost:8081"
    process.terminate()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    """Session for temporary PostgreSQL database."""
    Base.metadata.create_all(engine)
    # Mypy claims Session has no attribute __enter__, which is incorrect as
    # shown at
    # https://github.com/sqlalchemy/sqlalchemy/blob/52e8545b2df312898d46f6a5b119675e8d0aa956/lib/sqlalchemy/orm/session.py#L1156.
    with Session(engine) as session:  # type: ignore
        yield session
