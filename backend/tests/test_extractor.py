"""Runnable smoke test for the Phase 3 extractor.

Usage:
    .venv/bin/python -m backend.tests.test_extractor
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from backend.extractor.section_extractor import extract

FIXTURE = Path(__file__).parent / "fixtures" / "special_offer_popup.html"


def _expect(condition: bool, msg: str, failures: list[str]) -> None:
    if not condition:
        failures.append(msg)


def main() -> int:
    html = FIXTURE.read_text(encoding="utf-8")
    page = extract(html, page_title="BrandCo - Cosy Bedding")
    failures: list[str] = []

    _expect(page.text_length > 200, f"visible_text too short ({page.text_length} chars)", failures)
    _expect(
        "no thanks, i don't like saving money" in page.visible_text.lower(),
        "decline-link text missing from visible_text",
        failures,
    )
    _expect(
        any("save" in (b.text or "").lower() for b in page.buttons)
        or any("no thanks" in (b.text or "").lower() for b in page.buttons),
        "expected the styled-as-button decline anchor among buttons",
        failures,
    )

    accept_btn = next((b for b in page.buttons if "accept" in (b.text or "").lower()), None)
    reject_btn = next((b for b in page.buttons if "reject" in (b.text or "").lower()), None)
    _expect(accept_btn is not None, "Accept All button not extracted", failures)
    _expect(reject_btn is not None, "Reject button not extracted", failures)

    preselected = [c for c in page.checkboxes if c.checked]
    not_preselected = [c for c in page.checkboxes if not c.checked]
    _expect(len(preselected) == 2, f"expected 2 pre-checked checkboxes, got {len(preselected)}", failures)
    _expect(len(not_preselected) == 1, f"expected 1 unchecked checkbox, got {len(not_preselected)}", failures)
    _expect(
        any("marketing" in (c.label or "").lower() for c in preselected),
        "preselected newsletter checkbox should have a marketing-related label",
        failures,
    )

    _expect(len(page.cookie_banners) >= 1, "cookie banner not detected", failures)
    _expect(len(page.modals) >= 1, "modal not detected", failures)
    _expect(len(page.countdowns) >= 1, "countdown banner not detected", failures)
    _expect(
        any("ends in" in s.text.lower() or "deal" in s.text.lower() for s in page.countdowns),
        "countdown text content missing",
        failures,
    )

    summary = {
        "page_title": page.page_title,
        "text_length": page.text_length,
        "buttons": [(b.tag, b.text[:40]) for b in page.buttons],
        "checkboxes": [(c.label[:40], c.checked) for c in page.checkboxes],
        "cookie_banners": [s.text[:80] for s in page.cookie_banners],
        "modals": [s.text[:80] for s in page.modals],
        "countdowns": [s.text[:80] for s in page.countdowns],
    }
    print(json.dumps(summary, indent=2))

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll extractor checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
