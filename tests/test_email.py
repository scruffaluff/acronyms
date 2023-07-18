"""Tests for email integration."""


from typing import Dict

from playwright.sync_api import Page, expect
import pytest

from acronyms import mail


@pytest.mark.e2e
def test_send_email(server: Dict[str, str], page: Page) -> None:
    """Sent email appears in user interface."""
    page.goto(server["email"])
    email_list = page.locator("ul.email-list")
    list_item = email_list.locator('li:has-text("Test Email")')
    expect(list_item).to_have_count(0)

    mail.sender.cache_clear()
    mail.sender().send(
        subject="Test Email",
        sender="sender@mail.com",
        receivers=["reciever@mail.com"],
        text="This email was send by the test_send_email test.",
    )
    expect(list_item).to_have_count(1)
