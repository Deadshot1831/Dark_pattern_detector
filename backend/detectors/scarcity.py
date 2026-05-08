"""Scarcity detection.

The dataset has 679 scarcity rows. 'only N left' dominates (632 rows alone).
Patterns are organised low-stock vs high-demand to mirror the dataset taxonomy.
"""
from __future__ import annotations

import re
from typing import List

from ..extractor.section_extractor import ExtractedPage
from .base import BaseDetector, DetectionResult

SCARCITY_PATTERNS: List[tuple[str, float, str]] = [
    # Low-stock (numeric)
    (r"\bonly\s+\d+\s+(?:item|items)?\s*left(?:\s+in\s+stock)?\b", 0.92, "high"),
    (r"\bonly\s+\d+\s+(?:remaining|in\s+stock|available)\b", 0.9, "high"),
    (r"\bhurry,?\s+only\s+\d+\b", 0.92, "high"),
    (r"\b\d+\s+left\s+(?:in\s+stock|in\s+inventory|available)\b", 0.85, "medium"),
    # Low-stock (qualitative)
    (r"\b(selling\s+fast|going\s+fast|almost\s+gone|very\s+low\s+stock|low\s+stock|stock\s+(?:is|running)\s+low|running\s+out|few\s+left|limited\s+stock|limited\s+supply)\b", 0.82, "medium"),
    # High-demand
    (r"\b(in\s+high\s+demand|high\s+demand|will\s+sell\s+out|sell\s+out\s+fast|won'?t\s+last\s+long|once\s+it'?s\s+gone)\b", 0.82, "medium"),
    (r"\b(an\s+item\s+you\s+ordered\s+is|item\s+in\s+your\s+cart\s+is)\s+(?:popular|in\s+demand|selling)", 0.8, "medium"),
    # Activity / social proof framed as scarcity
    (r"\b\d+\s+(?:people|customers|users|others?)\s+(?:viewing|are\s+viewing|added|bought|are\s+looking\s+at)\b", 0.7, "low"),
    (r"\b\d+\s+(?:people|customers|users)\s+viewed\s+this\b", 0.7, "low"),
]

SUGGESTED_FIX = (
    "Show real, accurate stock counts only. If you don't have a stock signal, omit the message — "
    "don't fabricate scarcity. Avoid social-proof banners that imply scarcity by counting viewers."
)


class ScarcityDetector(BaseDetector):
    pattern_type = "scarcity"
    MAX_RESULTS = 6

    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        out: List[DetectionResult] = []
        seen_keys: set[str] = set()
        text = page.visible_text

        for pattern, conf, sev in SCARCITY_PATTERNS:
            for m in re.finditer(pattern, text, re.I):
                key = m.group(0).lower()
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                start = max(m.start() - 25, 0)
                end = min(m.end() + 35, len(text))
                out.append(DetectionResult(
                    pattern_type=self.pattern_type,
                    evidence_text=text[start:end].strip(),
                    evidence_selector="",
                    confidence=conf,
                    severity=sev,
                    explanation=f"Scarcity phrase detected: '{m.group(0)}'.",
                    suggested_fix=SUGGESTED_FIX,
                    method="rule",
                ))
                if len(out) >= self.MAX_RESULTS:
                    return out
        return out
