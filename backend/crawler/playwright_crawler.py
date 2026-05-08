from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

DEFAULT_USER_AGENT = "DeceptiTechBot/0.1 (+research; contact via project repo)"
NAV_TIMEOUT_MS = 30_000
SETTLE_MS = 1_500
VIEWPORT = {"width": 1366, "height": 800}


@dataclass
class CrawlResult:
    url: str
    final_url: str
    title: str
    html: str
    full_page_screenshot: Path
    viewport_screenshot: Path


async def crawl_url(url: str, screenshot_dir: Path) -> CrawlResult:
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    full_page_path = screenshot_dir / "full_page.png"
    viewport_path = screenshot_dir / "viewport.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport=VIEWPORT,
        )
        page = await context.new_page()
        try:
            try:
                await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
            except PlaywrightTimeoutError:
                await page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)

            await page.wait_for_timeout(SETTLE_MS)

            title = await page.title()
            html = await page.content()
            final_url = page.url

            await page.screenshot(path=str(viewport_path), full_page=False)
            await page.screenshot(path=str(full_page_path), full_page=True)
        finally:
            await context.close()
            await browser.close()

    return CrawlResult(
        url=url,
        final_url=final_url,
        title=title,
        html=html,
        full_page_screenshot=full_page_path,
        viewport_screenshot=viewport_path,
    )
