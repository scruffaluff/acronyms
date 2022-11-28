"""Resuable testing fixtures for acronyms."""


from argparse import BooleanOptionalAction
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
from pytest_mock import MockerFixture
from sqlalchemy.ext import asyncio

from tests import util


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
        port = util.find_port()
        url = f"http://localhost:{port}"
        environment = {"ACRONYMS_DATABASE": f"sqlite+aiosqlite:///{database}"}

        # Running the server via uvicorn directly as a Python function throws
        # "RuntimeError: asyncio.run() cannot be called from a running event
        # loop".
        process = Popen(
            ["acronyms", "--port", str(port)],
            env={**os.environ, **util.mock_environment(environment)},
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

        util.wait_for_server(url)
        yield url
        process.terminate()
        database.unlink()
