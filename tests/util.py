"""Utility functions for configuring tests."""


import socket
from typing import cast

from requests import Session
from requests.adapters import HTTPAdapter, Retry


def find_port() -> int:
    """Find an available free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return cast(int, sock.getsockname()[1])


def wait_for_server(url: str) -> None:
    """Retry requesting server until it is available."""
    with Session() as session:
        retries = Retry(total=4, backoff_factor=1)
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.get(url)
