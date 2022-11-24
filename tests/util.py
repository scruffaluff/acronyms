"""Utility functions for configuring tests."""


import json
import logging
from pathlib import Path
import socket
from typing import cast

import requests
from requests import Session
from requests.adapters import HTTPAdapter, Retry


def find_port() -> int:
    """Find an available free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return cast(int, sock.getsockname()[1])


def upload_acronyms(endpoint: str) -> None:
    """Import acronyms to backend for easier manual frontend interaction."""
    data_path = Path(__file__).parents[1] / "tests/data/acronyms.json"
    acronyms = json.loads(data_path.read_text())

    with Session() as session:
        for acronym in acronyms:
            response = session.post(f"{endpoint}/api/acronym", json=acronym)
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
