"""Runnable smoke test for Phase 4 detectors against the popup fixture.

Usage:
    .venv/bin/python -m backend.tests.test_detectors
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from backend.detectors.base import overall_severity
from backend.detectors.registry import run_all
from backend.extractor.section_extractor import extract

FIXTURE = Path(__file__).parent / "fixtures" / "special_offer_popup.html"


def _expect(condition: bool, msg: str, failures: list[str]) -> None:
    if not condition:
        failures.append(msg)


def main() -> int:
    html = FIXTURE.read_text(encoding="utf-8")
    page = extract(html, page_title="BrandCo - Cosy Bedding")
    detections = run_all(page)

    by_type = Counter(d.pattern_type for d in detections)

    print(f"Total detections: {len(detections)}")
    print(f"Overall severity: {overall_severity(detections)}")
    print("\nBreakdown by pattern_type:")
    for k, v in sorted(by_type.items()):
        print(f"  {v}× {k}")

    print("\nFindings:")
    for d in detections:
        print(f"  [{d.severity:>6}] {d.pattern_type:<22} conf={d.confidence:.2f} method={d.method:<6} :: {d.evidence_text[:90]}")

    failures: list[str] = []
    _expect(by_type["fake_urgency"] >= 1, "expected at least 1 fake_urgency detection", failures)
    _expect(by_type["scarcity"] >= 1, "expected at least 1 scarcity detection", failures)
    _expect(by_type["confirmshaming"] >= 1, "expected at least 1 confirmshaming detection", failures)
    _expect(by_type["preselected_options"] >= 2, f"expected ≥2 preselected detections, got {by_type['preselected_options']}", failures)
    _expect(by_type["cookie_manipulation"] >= 1, "expected at least 1 cookie_manipulation detection", failures)
    _expect(overall_severity(detections) == "high", "overall severity should be 'high'", failures)
    _expect(
        any("no thanks" in d.evidence_text.lower() for d in detections if d.pattern_type == "confirmshaming"),
        "confirmshaming evidence should contain 'no thanks'",
        failures,
    )
    _expect(
        any("only 2 left" in d.evidence_text.lower() for d in detections if d.pattern_type == "scarcity"),
        "scarcity evidence should contain 'only 2 left'",
        failures,
    )
    _expect(
        any("warranty" in d.evidence_text.lower() and d.severity == "high" for d in detections if d.pattern_type == "preselected_options"),
        "preselected paid add-on (warranty) should be HIGH severity",
        failures,
    )

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll detector checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
