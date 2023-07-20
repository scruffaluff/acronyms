"""Unit tests for authentication."""


import secrets
from typing import Tuple

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture


def test_login(
    client: TestClient, user: Tuple[str, str], mocker: MockerFixture
) -> None:
    """New regular user is able to login."""
    response = client.post(
        "/auth/login",
        data={"username": user[0], "password": user[1]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    result = response.json()

    assert result["token_type"] == "bearer"


def test_profile(
    client: TestClient, access_token: str, mocker: MockerFixture
) -> None:
    """Access token allows for querying of user information."""
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    response.raise_for_status()
    result = response.json()

    assert result["email"] == "basic.user@mail.com"
    assert result["is_active"]
    assert not result["is_superuser"]


def test_register(client: TestClient, mocker: MockerFixture) -> None:
    """New regular user is able to register."""
    mocker.patch("redmail.EmailSender.send")

    password = secrets.token_urlsafe(16)
    body = {"email": "basic.user@mail.com", "password": password}
    response = client.post("/auth/register", json=body)
    response.raise_for_status()
    result = response.json()

    assert result["is_active"]
    assert not result["is_superuser"]
