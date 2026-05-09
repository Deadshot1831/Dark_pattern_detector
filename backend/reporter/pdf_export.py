"""Render an HTML string to PDF bytes using the Playwright Chromium we already
ship with the backend. No new dependencies — Chrome's print engine is the PDF
engine.
"""
from __future__ import annotations

from playwright.async_api import async_playwright


async def html_to_pdf(html: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded")
            return await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "18mm", "bottom": "18mm", "left": "14mm", "right": "14mm"},
            )
        finally:
            await browser.close()
