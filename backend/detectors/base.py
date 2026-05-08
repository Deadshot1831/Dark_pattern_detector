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
