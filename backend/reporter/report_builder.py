"""Build a structured, JSON-serialisable report from a Scan record.

The report combines:
  - scan metadata (URL, title, timing)
  - the rolled-up severity + total counts
  - aggregate breakdowns (by_pattern_type / by_severity / by_method)
  - the full detection list, sorted high→low severity then by confidence
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Dict

from ..db.models import Scan

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def _severity_rank(s: str) -> int:
    return SEVERITY_ORDER.get(s, 0)


def _duration_seconds(scan: Scan) -> float | None:
    if scan.completed_at and scan.started_at:
        return round((scan.completed_at - scan.started_at).total_seconds(), 2)
    return None


def build_report_dict(scan: Scan) -> Dict[str, Any]:
    detections = sorted(
        scan.detections,
        key=lambda d: (_severity_rank(d.severity.value), d.confidence),
        reverse=True,
    )

    by_type = Counter(d.pattern_type for d in detections)
    by_severity = Counter(d.severity.value for d in detections)
    by_method = Counter(d.method for d in detections)

    return {
        "scan_id": scan.id,
        "url": scan.url,
        "final_url": scan.final_url,
        "page_title": scan.page_title,
        "status": scan.status.value,
        "scanned_at": scan.started_at.isoformat() if scan.started_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "duration_seconds": _duration_seconds(scan),
        "overall_severity": scan.overall_severity.value if scan.overall_severity else None,
        "total_patterns_found": scan.total_patterns_found or 0,
        "summary": {
            "by_pattern_type": dict(by_type),
            "by_severity": dict(by_severity),
            "by_method": dict(by_method),
        },
        "detections": [
            {
                "id": d.id,
                "pattern_type": d.pattern_type,
                "severity": d.severity.value,
                "confidence": round(d.confidence, 4),
                "evidence_text": d.evidence_text,
                "evidence_selector": d.evidence_selector,
                "explanation": d.explanation,
                "suggested_fix": d.suggested_fix,
                "method": d.method,
            }
            for d in detections
        ],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tool": {"name": "DeceptiTech", "version": "0.1.0"},
    }
