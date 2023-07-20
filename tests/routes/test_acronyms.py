"""Tests for acronym routes."""


from fastapi.testclient import TestClient
from httpx import HTTPStatusError
import pytest


def test_delete_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    get_response_1 = client.get("/api/acronym")
    get_response_1.raise_for_status()
    assert 1 in [acronym["id"] for acronym in get_response_1.json()]

    delete_response = client.delete("/api/acronym/1")
    delete_response.raise_for_status()

    get_response_2 = client.get("/api/acronym")
    get_response_2.raise_for_status()
    assert 1 not in [acronym["id"] for acronym in get_response_2.json()]


def test_delete_missing_acronym(client: TestClient) -> None:
    """Deletion of a nonexistant acronym throws an HTTP 404 Error."""
    response = client.delete("/api/acronym/9999")
    with pytest.raises(HTTPStatusError):
        response.raise_for_status()


def test_get_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    expected = [
        {
            "id": 3,
            "abbreviation": "DM",
            "description": None,
            "phrase": "Data Mining",
        },
        {
            "id": 4,
            "abbreviation": "DM",
            "description": None,
            "phrase": "Direct Message",
        },
    ]

    response = client.get("/api/acronym/?abbreviation=DM")
    response.raise_for_status()
    assert response.json() == expected


def test_get_acronym_id_error(client: TestClient) -> None:
    """Error response if Id is not in database."""
    response = client.get("/api/acronym?id=0")
    with pytest.raises(HTTPStatusError):
        response.raise_for_status()


def test_get_pagination_default(client: TestClient) -> None:
    """Acronym fetches are paginated."""
    response = client.get("/api/acronym")
    response.raise_for_status()
    assert len(response.json()) == 10


def test_get_acronym_error(client: TestClient) -> None:
    """Invalid query parameters are rejected."""
    response = client.get("/api/acronym?limit=100")
    with pytest.raises(HTTPStatusError):
        response.raise_for_status()


def test_get_pagination_offset(client: TestClient) -> None:
    """Acronym fetches are paginated."""
    response = client.get("/api/acronym?offset=10")
    response.raise_for_status()
    assert len(response.json()) == 6


def test_post_acronym(client: TestClient) -> None:
    """Add a new acronym to database."""
    body = {"abbreviation": "ROI", "phrase": "Return On Investment"}
    params = "&".join(f"{key}={value}" for key, value in body.items())

    get_response_1 = client.get(f"/api/acronym?{params}")
    get_response_1.raise_for_status()
    count = len(get_response_1.json())

    post_response = client.post("/api/acronym", json=body)
    post_response.raise_for_status()

    get_response_2 = client.get(f"/api/acronym?{params}")
    get_response_2.raise_for_status()
    assert len(get_response_2.json()) == count + 1


def test_post_duplicate(client: TestClient) -> None:
    """Adding a duplicate acronym receives an HTTP error."""
    body = {"abbreviation": "ROI", "phrase": "Return On Investment"}
    response_1 = client.post("/api/acronym", json=body)
    response_1.raise_for_status()

    response_2 = client.post("/api/acronym", json=body)
    with pytest.raises(HTTPStatusError):
        response_2.raise_for_status()


def test_put_acronym(client: TestClient) -> None:
    """Update acronym values."""
    get_response_1 = client.get("/api/acronym?id=1")
    get_response_1.raise_for_status()
    assert get_response_1.json()["phrase"] == "Ante Meridiem"

    body = {"abbreviation": "AM", "phrase": "Amplitude Modulation"}
    body_response = client.put("/api/acronym/1", json=body)
    body_response.raise_for_status()

    get_response_1 = client.get("/api/acronym?id=1")
    get_response_1.raise_for_status()
    assert get_response_1.json()["phrase"] == "Amplitude Modulation"


def test_put_duplicate(client: TestClient) -> None:
    """Editing an acronym to a duplicate value receives an HTTP error."""
    get_response = client.get("/api/acronym?id=1")
    get_response.raise_for_status()

    body = {
        key: value for key, value in get_response.json().items() if key != "id"
    }
    put_response = client.put("/api/acronym/2", json=body)
    with pytest.raises(HTTPStatusError):
        put_response.raise_for_status()
