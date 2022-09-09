"""Unit tests for acronyms."""


from typing import cast

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from acronyms.models import Acronym


def test_delete_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    response = client.get("/api")
    assert response.status_code == 200
    assert 1 in [acronym["id"] for acronym in response.json()]

    response = client.delete("/api/1")
    assert response.status_code == 200

    response = client.get("/api")
    assert response.status_code == 200
    assert 1 not in [acronym["id"] for acronym in response.json()]


def test_get_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    expected = [
        {"id": 2, "abbreviation": "DM", "expansion": "Data Mining"},
        {"id": 3, "abbreviation": "DM", "expansion": "Direct Message"},
    ]

    response = client.get("/api?abbreviation=DM")
    assert response.status_code == 200
    assert response.json() == expected


def test_post_acronym(client: TestClient) -> None:
    """Add a new acronym to database."""
    pre_response = client.get("/api")
    assert pre_response.status_code == 200
    records = len(pre_response.json())

    body = {"abbreviation": "ROI", "expansion": "Return On Investment"}
    post_response = client.post("/api", json=body)
    assert post_response.status_code == 200

    get_response = client.get("/api")
    assert get_response.status_code == 200
    assert len(get_response.json()) == records + 1


def test_query_acronym(database: Session) -> None:
    """Fetch acronym from database by abbreviation."""
    result = cast(
        Acronym,
        database.query(Acronym).filter(Acronym.abbreviation == "AM").first(),
    )
    assert result.expansion == "Ante Meridiem"


def test_put_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    response = client.get("/api?id=1")
    assert response.status_code == 200
    assert response.json()["expansion"] == "Ante Meridiem"

    body = {"abbreviation": "AM", "expansion": "Amplitude Modulation"}
    response = client.put("/api/1", json=body)
    assert response.status_code == 200

    response = client.get("/api?id=1")
    assert response.status_code == 200
    assert response.json()["expansion"] == "Amplitude Modulation"
