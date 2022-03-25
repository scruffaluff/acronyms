"""Unit tests for acronyms."""


from typing import cast

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from acronyms.models import Acronym


def test_get_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    expected = [
        {"abbreviation": "DM", "expansion": "Data Mining"},
        {"abbreviation": "DM", "expansion": "Direct Message"},
    ]

    response = client.get("/acronyms?abbreviation=DM")
    assert response.status_code == 200
    assert response.json() == expected


def test_post_acronym(client: TestClient) -> None:
    """Add a new acronym to database."""
    pre_response = client.get("/acronyms")
    assert pre_response.status_code == 200
    records = len(pre_response.json())

    body = {"abbreviation": "ROI", "expansion": "Return On Investment"}
    post_response = client.post("/acronyms", json=body)
    assert post_response.status_code == 200

    get_response = client.get("/acronyms")
    assert get_response.status_code == 200
    assert len(get_response.json()) == records + 1


def test_query_acronym(database: Session) -> None:
    """Fetch acronym from database by abbreviation."""
    result = cast(
        Acronym,
        database.query(Acronym).filter(Acronym.abbreviation == "AM").first(),
    )
    assert result.expansion == "Ante Meridiem"
