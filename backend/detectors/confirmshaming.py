"""Confirmshaming — shame-laden decline buttons.

Mined from 169 confirmshaming rows. The dominant patterns all start with
'No thanks, I…' or 'No, I don't…' followed by self-deprecating phrasing.
Operates on the *buttons* list (which already includes anchor decline links
inside modals), not on the whole visible_text — this avoids flagging legitimate
negative phrasing in body copy.
"""
from __future__ import annotations

import re
from typing import List

from ..extractor.section_extractor import ExtractedPage
from .base import BaseDetector, DetectionResult

CONFIRMSHAMING_PATTERNS: List[tuple[str, float]] = [
    (r"^\s*no[,\s]+thanks?[,\s]+i\s*(?:'?ll|'?d|don'?t|hate|prefer|like)\b", 0.95),
    (r"^\s*no[,\s]+i\s*(?:don'?t|hate|'?ll|'?d|prefer)\s*(?:want|need|feel|like|wish|care|enjoy|to)\b", 0.92),
    (r"\bi'?ll\s+pay\s+full\s+price\b", 0.95),
    (r"\bi\s+hate\s+(?:saving|deals|discounts|free\s+stuff|free\s+shipping)\b", 0.95),
    (r"\bi\s+don'?t\s+(?:want|need|like)\s+to\s+(?:save|win|get\s+a\s+deal|get\s+free)\b", 0.95),
    (r"\bi\s+(?:already|just)\s+(?:pay|spend)\s+(?:full|too\s+much|enough)\b", 0.85),
    (r"\bi\s+(?:prefer|enjoy|love)\s+(?:paying|missing\s+out|to\s+pay)\b", 0.9),
    (r"\bi\s+don'?t\s+(?:like|care\s+about)\s+(?:saving|free|gifts|discounts)\b", 0.93),
    (r"\bno\s+thanks?,?\s+i'?m\s+(?:not\s+interested|fine|good)\s+(?:in\s+saving|with\s+full\s+price)\b", 0.9),
]

SUGGESTED_FIX = (
    "Use neutral, respectful decline copy: 'No thanks', 'Maybe later', 'Skip', 'Close'. "
    "Avoid wording that mocks, guilt-trips or shames the user for declining."
)


class ConfirmshamingDetector(BaseDetector):
    pattern_type = "confirmshaming"

    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        out: List[DetectionResult] = []
        seen: set[str] = set()
        for btn in page.buttons:
            text = (btn.text or "").strip()
            if not text or len(text) > 200:
                continue
            key = text.lower()
            if key in seen:
                continue
            for pattern, conf in CONFIRMSHAMING_PATTERNS:
                if re.search(pattern, text, re.I):
                    seen.add(key)
                    out.append(DetectionResult(
                        pattern_type=self.pattern_type,
                        evidence_text=text,
                        evidence_selector=btn.selector,
                        confidence=conf,
                        severity="medium",
                        explanation=f"Decline control uses shaming language: '{text[:80]}'.",
                        suggested_fix=SUGGESTED_FIX,
                        method="rule",
                    ))
                    break
        return out
