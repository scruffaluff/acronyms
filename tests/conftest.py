"""Resuable testing fixtures for acronyms."""


from argparse import BooleanOptionalAction
import os
from pathlib import Path
import subprocess
import tempfile
from typing import cast, Iterator, Tuple

from _pytest.fixtures import SubRequest
from fastapi.testclient import TestClient
from psycopg import Connection
import pytest
from pytest import Parser
from pytest_mock import MockerFixture
import schemathesis
from schemathesis.specs.openapi.schemas import BaseOpenAPISchema
from sqlalchemy.ext import asyncio

from tests import util


@pytest.fixture
def access_token(client: TestClient, user: Tuple[str, str]) -> str:
    """Get access token for new user."""
    response = client.post(
        "/auth/login",
        data={"username": user[0], "password": user[1]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return cast(str, response.json()["access_token"])


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
def client(connection: str, mocker: MockerFixture) -> Iterator[TestClient]:
    """Fast API test client."""
    environment = util.mock_environment({"ACRONYMS_DATABASE": connection})
    mocker.patch.dict(os.environ, environment)
    mocker.patch(
        "acronyms.models.get_engine",
        lambda: asyncio.create_async_engine(connection, future=True),
    )

    from acronyms.main import app

    with TestClient(app) as client:
        util.upload_acronyms(client=client)
        yield client


@pytest.fixture
def connection(postgresql: Connection) -> str:
    """Connection URI for temporary PostgreSQL database."""
    user = postgresql.info.user
    address = f"{postgresql.info.host}:{postgresql.info.port}"
    name = postgresql.info.dbname
    return f"postgresql+asyncpg://{user}:@{address}/{name}"


@pytest.fixture(scope="session")
def openapi_schema() -> Iterator[BaseOpenAPISchema]:
    """Load OpenAPI schema from server into Schemathesis."""
    database = Path(tempfile.mkdtemp()) / "acronyms_test.db"
    backend, mail, url = util.start_server(database)
    yield schemathesis.from_uri(f"{url}/openapi.json")
    backend.terminate()
    mail.terminate()
    database.unlink()


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
        url = "https://acronyms.127-0-0-1.nip.io"
        util.clear_acronyms(url)
        yield url
    else:
        database = tmp_path / "acronyms_test.db"
        backend, mail, url = util.start_server(database)
        yield url
        backend.terminate()
        mail.terminate()
        database.unlink()


@pytest.fixture
def user(client: TestClient) -> Tuple[str, str]:
    """Create new user in application."""
    environment = util.mock_environment({})
    email = environment["ACRONYMS_SMTP_USERNAME"]
    password = environment["ACRONYMS_SMTP_PASSWORD"]

    response = client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    response.raise_for_status()
    return email, password
