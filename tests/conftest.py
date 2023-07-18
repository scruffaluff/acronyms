"""Resuable testing fixtures for acronyms."""


from argparse import BooleanOptionalAction
import secrets
import subprocess
from typing import Dict, Iterator, Tuple, cast

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
def client(mocker: MockerFixture) -> Iterator[TestClient]:
    """Fast API test client."""
    settings = util.mock_settings()
    mocker.patch("acronyms.settings.settings", lambda: settings)
    # TODO: Figure out better method to prevent get_engine from being cached
    # between test functions.
    mocker.patch(
        "acronyms.models.get_engine",
        lambda: asyncio.create_async_engine(settings.database, future=True),
    )
    mocker.patch("redmail.EmailSender.send")

    from acronyms.main import app

    with TestClient(app) as client:
        util.upload_acronyms(client=client)
        yield client


@pytest.fixture
def connection(postgresql: Connection) -> str:
    """Parse connection URI for temporary PostgreSQL database."""
    user = postgresql.info.user
    address = f"{postgresql.info.host}:{postgresql.info.port}"
    name = postgresql.info.dbname
    return f"postgresql+asyncpg://{user}:@{address}/{name}"


@pytest.fixture(scope="session")
def openapi_schema() -> Iterator[BaseOpenAPISchema]:
    """Load OpenAPI schema from server into Schemathesis."""
    settings = util.mock_settings()
    backend, mail = util.start_server(settings)

    yield schemathesis.from_uri(
        f"http://localhost:{settings.port}/openapi.json"
    )
    backend.terminate()
    mail.terminate()


def pytest_addoption(parser: Parser) -> None:
    """Add CLI flag options to test suite."""
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
def server(
    request: SubRequest, mocker: MockerFixture
) -> Iterator[Dict[str, str]]:
    """Compile frontend assets and start backend and mail servers."""
    if request.config.getoption("--chart"):
        url = "https://acronyms.127-0-0-1.nip.io"
        util.clear_acronyms(url)
        yield {"backend": url, "email": "https://mail.127-0-0-1.nip.io"}
    else:
        settings = util.mock_settings()
        mocker.patch("acronyms.settings.settings", lambda: settings)
        smtp_web_port = util.find_port()
        backend, mail = util.start_server(settings, smtp_web_port)

        yield {
            "backend": f"http://localhost:{settings.port}",
            "email": f"http://localhost:{smtp_web_port}",
            "process": [backend, mail],  # type: ignore
        }
        backend.terminate()
        mail.terminate()


@pytest.fixture
def user(client: TestClient) -> Tuple[str, str]:
    """Create new user in application."""
    email = "basic.user@mail.com"
    password = secrets.token_urlsafe(32)

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    return email, password
