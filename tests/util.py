"""Utility functions for configuring tests."""


import json
import logging
from pathlib import Path
import secrets
import socket
from typing import cast, Dict, Optional

from fastapi.testclient import TestClient
import requests
from requests import Session
from requests.adapters import HTTPAdapter, Retry


DATA_PATH = Path(__file__).parent / "data"


def clear_acronyms(server: str) -> None:
    """Remove all acronyms from server."""
    response = requests.get(f"{server}/api/acronym")
    response.raise_for_status()

    for acronym in response.json():
        id_ = acronym["id"]
        response_ = requests.delete(f"{server}/api/acronym/{id_}")
        response_.raise_for_status()


def find_port() -> int:
    """Find an available free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return cast(int, sock.getsockname()[1])


def mock_environment(variables: Dict[str, str]) -> Dict[str, str]:
    """Generate mock environment variables for testing."""
    return {
        **{
            "ACRONYMS_RESET_TOKEN": secrets.token_urlsafe(64),
            "ACRONYMS_VERIFICATION_TOKEN": secrets.token_urlsafe(64),
        },
        **variables,
    }


def upload_acronyms(
    client: Optional[TestClient] = None, endpoint: Optional[str] = None
) -> None:
    """Import acronyms to backend for easier manual frontend interaction."""
    data_path = DATA_PATH / "acronyms.json"
    acronyms = json.loads(data_path.read_text())

    if client is None:
        for acronym in acronyms:
            response = requests.post(f"{endpoint}/api/acronym", json=acronym)
            response.raise_for_status()
    else:
        for acronym in acronyms:
            response = client.post("/api/acronym", json=acronym)
            response.raise_for_status()


def wait_for_server(url: str) -> None:
    """Retry requesting server until it is available."""
    logging.getLogger(
        requests.packages.urllib3.__package__  # type: ignore
    ).setLevel(logging.ERROR)

    with Session() as session:
        retries = Retry(total=4, backoff_factor=1)
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.get(url)
