from __future__ import annotations

import os
import time
import traceback
from urllib.parse import urljoin, urlparse

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright


APP_INTERNAL_URL = "http://app:8000"
BOT_POLL_SECONDS = 2.0
BOT_IGNORE_HTTPS_ERRORS = True
VISIT_TOTAL_SECONDS = 10

BOT_INTERNAL_TOKEN = os.getenv("BOT_INTERNAL_TOKEN", "bot-dev-token")
FLAG_COOKIE_NAME = os.getenv("FLAG_COOKIE_NAME", "flag")
FLAG = os.getenv("FLAG", "")
BOT_VISIT_BASE_URL = os.getenv("BOT_VISIT_BASE_URL", APP_INTERNAL_URL)


def headers() -> dict[str, str]:
    return {"X-Bot-Token": BOT_INTERNAL_TOKEN}


def claim_job(session: requests.Session):
    response = session.post(f"{APP_INTERNAL_URL.rstrip('/')}/api/internal/bot/jobs/claim", headers=headers(), timeout=10)
    if response.status_code == 204:
        return None
    response.raise_for_status()
    return response.json()


def complete_job(session: requests.Session, chat_id: str, answer: str) -> None:
    response = session.post(
        f"{APP_INTERNAL_URL.rstrip('/')}/api/internal/bot/jobs/{chat_id}/complete",
        headers=headers(),
        json={"answer": answer},
        timeout=10,
    )
    response.raise_for_status()


def fail_job(session: requests.Session, chat_id: str) -> None:
    session.post(
        f"{APP_INTERNAL_URL.rstrip('/')}/api/internal/bot/jobs/{chat_id}/fail",
        headers=headers(),
        timeout=10,
    )


def flag_cookie() -> dict:
    return {
        "name": FLAG_COOKIE_NAME,
        "value": FLAG,
        "url": BOT_VISIT_BASE_URL.rstrip("/") + "/",
        "httpOnly": False,
        "secure": urlparse(BOT_VISIT_BASE_URL).scheme == "https",
        "sameSite": "Lax",
    }


def visit(url: str) -> None:
    visit_url = url if urlparse(url).scheme else urljoin(BOT_VISIT_BASE_URL.rstrip("/") + "/", url.lstrip("/"))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(ignore_https_errors=BOT_IGNORE_HTTPS_ERRORS)
            try:
                if FLAG_COOKIE_NAME and FLAG:
                    context.add_cookies([flag_cookie()])
                page = context.new_page()
                deadline = time.monotonic() + VISIT_TOTAL_SECONDS
                try:
                    page.goto(visit_url, wait_until="domcontentloaded", timeout=VISIT_TOTAL_SECONDS * 1000)
                except PlaywrightTimeoutError:
                    pass
                remaining_ms = max(0, int((deadline - time.monotonic()) * 1000))
                if remaining_ms:
                    page.wait_for_timeout(remaining_ms)
            finally:
                context.close()
        finally:
            browser.close()


def main() -> None:
    session = requests.Session()
    while True:
        job = None
        try:
            job = claim_job(session)
        except requests.RequestException as error:
            print(f"app unavailable, retrying: {error}", flush=True)
            time.sleep(BOT_POLL_SECONDS)
            continue

        try:
            if job:
                visit(job["url"])
                complete_job(session, job["id"], job["answer"])
        except Exception:
            traceback.print_exc()
            if job:
                fail_job(session, job["id"])
        time.sleep(BOT_POLL_SECONDS)


if __name__ == "__main__":
    main()
