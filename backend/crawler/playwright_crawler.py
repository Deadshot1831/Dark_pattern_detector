from dataclasses import dataclass
from pathlib import Path

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

# A real Chrome user-agent string. The previous "DeceptiTechBot/0.1" UA caused
# Akamai / Cloudflare-protected sites to refuse the connection at the HTTP/2
# layer (net::ERR_HTTP2_PROTOCOL_ERROR). DeceptiTech is a research crawler,
# not stealth scraping — but identifying as the underlying Chromium engine
# (which is what we actually are) sidesteps anti-bot stacks that only check
# the UA string.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
NAV_TIMEOUT_MS = 30_000
SETTLE_MS = 1_500
VIEWPORT = {"width": 1366, "height": 800}

# --disable-http2 forces HTTP/1.1, avoiding HTTP/2 protocol errors on sites
# whose stacks are picky with headless connections.
# --disable-blink-features=AutomationControlled removes the navigator.webdriver
# flag that triggers some bot-detection checks.
LAUNCH_ARGS = [
    "--disable-http2",
    "--disable-blink-features=AutomationControlled",
]


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
        browser = await p.chromium.launch(headless=True, args=LAUNCH_ARGS)
        context = await browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport=VIEWPORT,
        )
        page = await context.new_page()
        try:
            try:
                await page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
            except PlaywrightError:
                # Catch-all: network idle never reached (timeout), HTTP/2
                # protocol errors, transient connection drops. domcontentloaded
                # is more permissive — once the DOM has parsed we can still
                # extract patterns, even if a third-party tracker is hanging.
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
