"""Fake-urgency detection.

Patterns derived from the 481 Urgency rows of dark-patterns-v2.csv:
the dataset is dominated by "ends in", "limited time", "hurry", and HH:MM:SS
timer patterns, plus reservation phrases like "your cart is reserved".
"""
from __future__ import annotations

import re
from typing import List

from ..extractor.section_extractor import ExtractedPage
from .base import BaseDetector, DetectionResult, snippet_around

URGENCY_PATTERNS: List[tuple[str, float, str]] = [
    (r"\b(ends?\s+in|expires?\s+in|deal\s+ends|sale\s+ends|hurry\s+sale\s+ends)\b", 0.9, "high"),
    (r"\b(limited\s+time(?:\s+(?:only|offer))?|today\s+only|while\s+supplies\s+last|act\s+now)\b", 0.85, "high"),
    (r"\b(hurry|don'?t\s+miss|last\s+chance|going\s+fast|won'?t\s+last)\b", 0.75, "medium"),
    # HH:MM(:SS) explicit timers
    (r"\b\d{1,2}\s*:\s*\d{2}(?:\s*:\s*\d{2})?\b", 0.85, "high"),
    # "1 day 21h 04m 58s" style multi-unit countdowns
    (r"\b\d+\s*(?:days?|d|hrs?|hours?|h|mins?|minutes?|m|secs?|seconds?|s)\b\s*[: ]?\s*\d+\s*(?:days?|d|hrs?|hours?|h|mins?|minutes?|m|secs?|seconds?|s)\b", 0.8, "high"),
    # Reservation pressure
    (r"\b(?:cart|order|item|items)\s+(?:will\s+expire|is\s+reserved|are\s+reserved|will\s+be\s+reserved|expires?)", 0.9, "high"),
]

SUGGESTED_FIX = (
    "Remove false urgency cues. If a deadline is real, state it once in plain language "
    "(e.g. 'Sale ends Friday 6pm UTC') without an animated countdown. Never reset timers on refresh."
)


class FakeUrgencyDetector(BaseDetector):
    pattern_type = "fake_urgency"
    MAX_RESULTS = 6

    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        out: List[DetectionResult] = []
        seen_keys: set[str] = set()

        # 1. Structured countdown sections from the extractor
        for c in page.countdowns:
            key = c.text[:120].lower()
            if key in seen_keys:
                continue
            seen_keys.add(key)
            out.append(DetectionResult(
                pattern_type=self.pattern_type,
                evidence_text=c.text[:240],
                evidence_selector=c.selector,
                confidence=0.92,
                severity="high",
                explanation="A countdown timer / 'ends in' element was detected. Animated timers create artificial purchase pressure.",
                suggested_fix=SUGGESTED_FIX,
                method="hybrid",
            ))

        # 2. Visible-text regex sweep
        text = page.visible_text
        for pattern, conf, sev in URGENCY_PATTERNS:
            for m in re.finditer(pattern, text, re.I):
                key = m.group(0).lower()
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                out.append(DetectionResult(
                    pattern_type=self.pattern_type,
                    evidence_text=snippet_around(text, m.start(), m.end()),
                    evidence_selector="",
                    confidence=conf,
                    severity=sev,
                    explanation=f"Urgency phrase detected: '{m.group(0)}'.",
                    suggested_fix=SUGGESTED_FIX,
                    method="rule",
                ))
                if len(out) >= self.MAX_RESULTS:
                    return out
        return out
