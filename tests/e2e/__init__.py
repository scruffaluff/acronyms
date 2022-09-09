"""End to end tests for Acronyms."""


import re

from playwright.sync_api import expect, Page


def test_site_available(page: Page) -> None:
    """Website is available for external traffic."""
    page.goto("http://localhost:8000")
    expect(page).to_have_title(re.compile("Acronyms"))
