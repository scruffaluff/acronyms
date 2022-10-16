"""Unit tests for acronyms."""


import re
from typing import cast

from fastapi.testclient import TestClient
from playwright.sync_api import expect, Page
import pytest
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from acronyms.models import Acronym


@pytest.mark.e2e
def test_add_acronym_valid(server: str, page: Page) -> None:
    """Add acronym process completes for valid acronym."""
    acronym = {"abbreviation": "AM", "phrase": "Amplitude Modulation"}
    table_text = re.compile(acronym["abbreviation"] + acronym["phrase"])
    page.goto(server)

    table_body = page.locator("data-testid=table-body")
    submit = page.locator(
        '[data-testid="table-body"] button:has-text("Submit")'
    )

    page.locator("#search").fill(acronym["phrase"])
    expect(table_body).not_to_have_text(table_text)
    page.locator("#add").click()
    expect(submit).to_be_visible()

    entry = page.locator("*:focus")
    entry.fill(acronym["abbreviation"])
    entry.press("Enter")
    expect(submit).not_to_be_visible()
    expect(table_body).to_have_text(table_text)


@pytest.mark.e2e
def test_add_acronym_invalid(server: str, page: Page) -> None:
    """Add acronym process is unable to complete for invalid acronym."""
    page.goto(server)
    page.locator("#add").click()
    submit = page.locator(
        '[data-testid="table-body"] button:has-text("Submit")'
    )

    entry = page.locator("*:focus")
    entry.press("Enter")
    expect(submit).to_be_visible()


@pytest.mark.e2e
def test_add_acronym_error(server: str, page: Page) -> None:
    """Error modal pops up upon erroneous acronym submission."""
    page.goto(server)

    page.locator("#search").fill("Error Handling")
    page.locator("#add").click()

    entry = page.locator("*:focus")
    entry.fill("EH")
    entry.press("Enter")

    page.locator("#search").fill("Error Handling")
    page.locator("#add").click()

    entry = page.locator("*:focus")
    entry.fill("EH")
    entry.press("Enter")
    expect(page.locator("#error-modal")).to_be_visible()


@pytest.mark.e2e
def test_begin_add_acronym_button(server: str, page: Page) -> None:
    """Clicking add button begins new acronym process."""
    page.goto(server)
    submit = page.locator(
        '[data-testid="table-body"] button:has-text("Submit")'
    )
    expect(submit).not_to_be_visible()

    page.locator("#add").click()
    expect(submit).to_be_visible()


@pytest.mark.e2e
def test_begin_add_acronym_keypress(server: str, page: Page) -> None:
    """Pressing keys while in search focus begins new acronym process."""
    page.goto(server)
    submit = page.locator(
        '[data-testid="table-body"] button:has-text("Submit")'
    )
    expect(submit).not_to_be_visible()

    search = page.locator("#search")
    search.press("Control+Enter")
    expect(submit).to_be_visible()


def test_delete_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    get_response_1 = client.get("/api")
    get_response_1.raise_for_status()
    assert 1 in [acronym["id"] for acronym in get_response_1.json()]

    delete_response = client.delete("/api/1")
    delete_response.raise_for_status()

    get_response_2 = client.get("/api")
    get_response_2.raise_for_status()
    assert 1 not in [acronym["id"] for acronym in get_response_2.json()]


def test_get_acronym(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    expected = [
        {"id": 2, "abbreviation": "DM", "phrase": "Data Mining"},
        {"id": 3, "abbreviation": "DM", "phrase": "Direct Message"},
    ]

    response = client.get("/api?abbreviation=DM")
    response.raise_for_status()
    assert response.json() == expected


def test_get_favicon(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    response = client.get("/favicon.ico")
    response.raise_for_status()
    assert response.headers["content-type"] == "image/vnd.microsoft.icon"


def test_get_home(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    response = client.get("/")
    response.raise_for_status()


def test_post_acronym(client: TestClient) -> None:
    """Add a new acronym to database."""
    get_response_1 = client.get("/api")
    get_response_1.raise_for_status()
    records = len(get_response_1.json())

    body = {"abbreviation": "ROI", "phrase": "Return On Investment"}
    post_response = client.post("/api", json=body)
    post_response.raise_for_status()

    get_response_2 = client.get("/api")
    get_response_2.raise_for_status()
    assert len(get_response_2.json()) == records + 1


def test_post_duplicate(client: TestClient) -> None:
    """Adding a duplicate acronym receives an HTTP error."""
    body = {"abbreviation": "ROI", "phrase": "Return On Investment"}
    response_1 = client.post("/api", json=body)
    response_1.raise_for_status()

    response_2 = client.post("/api", json=body)
    with pytest.raises(HTTPError):
        response_2.raise_for_status()


def test_query_acronym(database: Session) -> None:
    """Fetch acronym from database by abbreviation."""
    result = cast(
        Acronym,
        database.query(Acronym).filter(Acronym.abbreviation == "AM").first(),
    )
    assert result.phrase == "Ante Meridiem"


def test_put_acronym(client: TestClient) -> None:
    """Update acronym values."""
    get_response_1 = client.get("/api?id=1")
    get_response_1.raise_for_status()
    assert get_response_1.json()["phrase"] == "Ante Meridiem"

    body = {"abbreviation": "AM", "phrase": "Amplitude Modulation"}
    body_response = client.put("/api/1", json=body)
    body_response.raise_for_status()

    get_response_1 = client.get("/api?id=1")
    get_response_1.raise_for_status()
    assert get_response_1.json()["phrase"] == "Amplitude Modulation"


def test_put_duplicate(client: TestClient) -> None:
    """Editing an acronym to a duplicate value receives an HTTP error."""
    get_response = client.get("/api?id=1")
    get_response.raise_for_status()

    body = {
        key: value for key, value in get_response.json().items() if key != "id"
    }
    put_response = client.put("/api/2", json=body)
    with pytest.raises(HTTPError):
        put_response.raise_for_status()


@pytest.mark.e2e
def test_site_available(server: str, page: Page) -> None:
    """Website is available for external traffic."""
    page.goto(server)
    expect(page).to_have_title(re.compile("Acronyms"))
