"""Resuable testing fixtures for acronyms."""


from argparse import BooleanOptionalAction
import json
import os
from pathlib import Path
import subprocess
from subprocess import Popen
from typing import Iterator

from _pytest.fixtures import SubRequest
from fastapi.testclient import TestClient
from psycopg import Connection
import pytest
from pytest import Parser
import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from acronyms.models import Acronym, Base, get_db
from tests import util


DATA_PATH = Path(__file__).parent / "data"


@pytest.fixture(autouse=True, scope="session")
def build(request: SubRequest) -> None:
    """Build frontend assets before test suite."""
    if request.config.getoption("--build"):
        subprocess.run(
            ["npm", "run", "build"],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )


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
    acronyms = json.loads((DATA_PATH / "acronyms.json").read_text())
    for acronym in acronyms:
        session.add(Acronym(**acronym))
    session.commit()
    return session


@pytest.fixture
def engine(connection: str) -> Engine:
    """Engine for temporary PostgreSQL database."""
    return sqlalchemy.create_engine(connection)


def pytest_addoption(parser: Parser) -> None:
    """Select whether to run tests against Helm chart."""
    parser.addoption(
        "--build",
        action=BooleanOptionalAction,
        default=False,
        help="Whether to compile frontend code before executing tests",
    )

    parser.addoption(
        "--chart",
        action=BooleanOptionalAction,
        default=False,
        help="Whether to run tests against Helm chart",
    )


@pytest.fixture
def server(request: SubRequest, tmp_path: Path) -> Iterator[str]:
    """Compile frontend assets and starts backend server."""
    if request.config.getoption("--chart"):
        yield "https://acronyms.127-0-0-1.nip.io"
    else:
        database = tmp_path / "acronyms_test.db"
        port = util.find_port()
        url = f"http://localhost:{port}"

        # Running the server via uvicorn directly as a Python function throws
        # "RuntimeError: asyncio.run() cannot be called from a running event
        # loop".
        process = Popen(
            ["acronyms", "--port", str(port)],
            env=dict(
                **os.environ, **{"ACRONYMS_DATABASE": f"sqlite:///{database}"}
            ),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        util.wait_for_server(url)
        yield url
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
