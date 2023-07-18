"""Utility functions for configuring tests."""


import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
from subprocess import Popen
import tempfile
from typing import Dict, Optional, Tuple, cast

from fastapi.testclient import TestClient
import httpx
from httpx import Client, HTTPTransport

from acronyms.settings import DatabaseUrl, Settings


DATA_PATH = Path(__file__).parent / "data"


def clear_acronyms(server: str) -> None:
    """Remove all acronyms from server."""
    response = httpx.get(f"{server}/api/acronym")
    response.raise_for_status()

    for acronym in response.json():
        id_ = acronym["id"]
        response_ = httpx.delete(f"{server}/api/acronym/{id_}")
        response_.raise_for_status()


def find_port() -> int:
    """Find an available free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return cast(int, sock.getsockname()[1])


def mock_settings() -> Settings:
    """Generate application settings for test suite."""
    sqlite_path = Path(tempfile.mkdtemp()) / "acronyms_test.db"
    database = DatabaseUrl(
        f"sqlite+aiosqlite:///{sqlite_path}", scheme="sqlite"
    )
    server_port = find_port()
    smtp_port = find_port()

    return Settings(
        database=database,
        port=server_port,
        reset_token=secrets.token_urlsafe(64),
        smtp_enabled=True,
        smtp_host="localhost",
        smtp_password=secrets.token_urlsafe(32),
        smtp_port=smtp_port,
        smtp_tls=False,
        smtp_username="admin.user@mail.com",
        verification_token=secrets.token_urlsafe(64),
    )


def popen_stdio(process: Popen, file: str = "stdout") -> str:
    """Terminate process and get its IO."""
    process.terminate()
    stdio = getattr(process, file)
    return "\n".join(line.decode("utf-8") for line in stdio)


def settings_variables(settings: Settings) -> Dict[str, str]:
    """Convert settings to equivalent environment variables."""
    prefix = settings.Config.env_prefix
    config = {}
    for key, value in settings.dict().items():
        try:
            value_ = str(value.get_secret_value())
        except AttributeError:
            value_ = str(value)
        config[f"{prefix}{key}".upper()] = value_
    return config


def start_server(
    settings: Settings, smtp_web_port: int = 1080
) -> Tuple[Popen, Popen]:
    """Start server for testing."""
    mail = Popen(
        [
            "npx",
            "maildev",
            "--incoming-user",
            settings.smtp_username,
            "--incoming-pass",
            settings.smtp_password.get_secret_value(),
            "--smtp",
            str(settings.smtp_port),
            "--web",
            str(smtp_web_port),
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    mail.stdout_text = lambda: popen_stdio(mail, "stdout")  # type: ignore
    mail.stderr_text = lambda: popen_stdio(mail, "stderr")  # type: ignore

    # Running the server via uvicorn directly as a Python function throws
    # "RuntimeError: asyncio.run() cannot be called from a running event
    # loop".
    backend = Popen(
        ["acronyms", "--port", str(settings.port)],
        env={**os.environ, **settings_variables(settings)},
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    backend.stdout_text = lambda: popen_stdio(backend, "stdout")  # type: ignore
    backend.stderr_text = lambda: popen_stdio(backend, "stderr")  # type: ignore

    wait_for_server(f"http://localhost:{settings.port}")
    return backend, mail


def upload_acronyms(
    client: Optional[TestClient] = None, endpoint: Optional[str] = None
) -> None:
    """Import acronyms to backend for easier manual frontend interaction."""
    data_path = DATA_PATH / "acronyms.json"
    acronyms = json.loads(data_path.read_text())

    if client is None:
        for acronym in acronyms:
            response = httpx.post(f"{endpoint}/api/acronym", json=acronym)
            response.raise_for_status()
    else:
        for acronym in acronyms:
            response = client.post("/api/acronym", json=acronym)
            response.raise_for_status()


def wait_for_server(url: str) -> None:
    """Retry requesting server until it is available."""
    transport = HTTPTransport(retries=4)
    with Client(transport=transport) as client:
        client.get(url)
