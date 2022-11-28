"""Unit tests for acronyms."""


import re

from fastapi.testclient import TestClient
from playwright.sync_api import expect, Page
import pytest
import requests
from requests.exceptions import HTTPError

from tests import util


@pytest.mark.e2e
def test_add_acronym_valid(server: str, page: Page) -> None:
    """Add acronym process completes for valid acronym."""
    acronym = {"abbreviation": "AFK", "phrase": "Away From Keyboard"}
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
    """Error modal pops up upon duplicate acronym submission."""
    acronym = {"abbreviation": "ECC", "phrase": "Error Correction Code"}
    response = requests.post(f"{server}/api/acronym", json=acronym)
    response.raise_for_status()

    page.goto(server)
    page.locator("#search").fill(acronym["phrase"])
    page.locator("#add").click()

    entry = page.locator("*:focus")
    entry.fill(acronym["abbreviation"])
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
    get_response_1 = client.get("/api/acronym")
    get_response_1.raise_for_status()
    assert 1 in [acronym["id"] for acronym in get_response_1.json()]

    delete_response = client.delete("/api/acronym/1")
    delete_response.raise_for_status()

    get_response_2 = client.get("/api/acronym")
    get_response_2.raise_for_status()
    assert 1 not in [acronym["id"] for acronym in get_response_2.json()]


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


def test_get_pagination_default(client: TestClient) -> None:
    """Acronym fetches are paginated."""
    response = client.get("/api/acronym")
    response.raise_for_status()
    assert len(response.json()) == 10


def test_get_acronym_error(client: TestClient) -> None:
    """Fetch acronym from database by abbreviation."""
    response = client.get("/api/acronym?limit=100")
    with pytest.raises(HTTPError):
        response.raise_for_status()


def test_get_pagination_offset(client: TestClient) -> None:
    """Acronym fetches are paginated."""
    response = client.get("/api/acronym?offset=10")
    response.raise_for_status()
    assert len(response.json()) == 6


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
    with pytest.raises(HTTPError):
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
    with pytest.raises(HTTPError):
        put_response.raise_for_status()


@pytest.mark.e2e
def test_site_available(server: str, page: Page) -> None:
    """Website is available for external traffic."""
    page.goto(server)
    expect(page).to_have_title(re.compile("Acronyms"))


@pytest.mark.e2e
def test_search_acronyms(server: str, page: Page) -> None:
    """Search finds results from all pages and changes page count."""
    phrase = "Physical Therapist"
    util.upload_acronyms(endpoint=server)

    page.goto(server)
    table_body = page.locator("data-testid=table-body")

    page.locator("#search").fill(phrase.split(" ")[0])
    expect(table_body).to_have_text(re.compile(phrase))

    pages = page.locator('[data-testid="pages"] > li')
    expect(pages).to_have_count(1)


@pytest.mark.e2e
def test_sort_acronyms(server: str, page: Page) -> None:
    """Sort icon changes acronym order."""
    acronyms = [
        {"abbreviation": "DM", "phrase": "Data Mining"},
        {"abbreviation": "DM", "phrase": "Direct Message"},
    ]
    for acronym in acronyms:
        response = requests.post(f"{server}/api/acronym", json=acronym)
        response.raise_for_status()

    page.goto(server)
    table_body = page.locator("data-testid=table-body")
    expect(table_body).to_have_text(re.compile("DMData MiningDMDirect Message"))

    page.locator("#phrase-sort").click()
    expect(table_body).to_have_text(re.compile("DMDirect MessageDMData Mining"))
