"""Open browser to initialize security database for Mkcert."""


from playwright import sync_api


with sync_api.sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.wikipedia.org")
