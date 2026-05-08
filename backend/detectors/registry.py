from __future__ import annotations

from typing import List

from ..extractor.section_extractor import ExtractedPage
from .base import BaseDetector, DetectionResult
from .confirmshaming import ConfirmshamingDetector
from .cookie_manipulation import CookieManipulationDetector
from .fake_urgency import FakeUrgencyDetector
from .preselected_options import PreselectedOptionDetector
from .scarcity import ScarcityDetector

DEFAULT_DETECTORS: List[BaseDetector] = [
    FakeUrgencyDetector(),
    ScarcityDetector(),
    ConfirmshamingDetector(),
    PreselectedOptionDetector(),
    CookieManipulationDetector(),
]


def run_all(page: ExtractedPage) -> List[DetectionResult]:
    out: List[DetectionResult] = []
    for det in DEFAULT_DETECTORS:
        try:
            out.extend(det.detect(page))
        except Exception as e:  # one detector should never break the others
            out.append(DetectionResult(
                pattern_type=det.pattern_type,
                evidence_text=f"<detector error: {type(e).__name__}: {e}>",
                evidence_selector="",
                confidence=0.0,
                severity="low",
                explanation="An internal detector error occurred. The page was not analysed for this pattern.",
                suggested_fix="",
                method="rule",
            ))
    return out
