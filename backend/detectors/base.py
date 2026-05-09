from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import List

from ..extractor.section_extractor import ExtractedPage

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass
class DetectionResult:
    pattern_type: str
    evidence_text: str
    evidence_selector: str
    confidence: float
    severity: str
    explanation: str
    suggested_fix: str
    method: str

    def to_dict(self) -> dict:
        return asdict(self)


class BaseDetector(ABC):
    pattern_type: str = "unknown"

    @abstractmethod
    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        ...


def overall_severity(detections: List[DetectionResult]) -> str:
    """The most severe single finding decides the page's overall severity."""
    if not detections:
        return "low"
    worst = max(SEVERITY_ORDER[d.severity] for d in detections)
    return next(k for k, v in SEVERITY_ORDER.items() if v == worst)


def snippet_around(
    text: str, match_start: int, match_end: int, padding: int = 40
) -> str:
    """Return the matched substring + surrounding context, snapped to word
    boundaries so we never cut mid-word.

    Adds an ellipsis when the snippet is truncated. Used by every
    visible-text detector so detections shown in the report read as full
    phrases rather than ``"n Amazon Devices … Limited tim"`` slices.
    """
    n = len(text)
    start = max(match_start - padding, 0)
    end = min(match_end + padding, n)

    # Snap left boundary forward to the first whitespace before the match,
    # then past that whitespace.
    if start > 0:
        while start < match_start and not text[start].isspace():
            start += 1
        while start < match_start and text[start].isspace():
            start += 1

    # Snap right boundary backward to the last whitespace after the match.
    if end < n:
        while end > match_end and not text[end - 1].isspace():
            end -= 1
        while end > match_end and text[end - 1].isspace():
            end -= 1

    snippet = text[start:end].strip()
    if start > 0:
        snippet = "… " + snippet
    if end < n:
        snippet = snippet + " …"
    return snippet
