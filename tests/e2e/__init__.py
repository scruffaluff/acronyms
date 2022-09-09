"""End to end tests for Acronyms."""


import re

from playwright.sync_api import expect, Page


def test_site_available(page: Page) -> None:
    """Website is available for external traffic."""
    page.goto("https://acronyms.127-0-0-1.nip.io")
    expect(page).to_have_title(re.compile("Acronyms"))
