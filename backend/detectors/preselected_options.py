"""Preselected option detection — pure DOM / structure based.

Flags any pre-checked checkbox whose label hints at marketing opt-ins or paid
add-ons. We deliberately skip neutral required boxes ('I accept the terms')
to avoid false positives.
"""
from __future__ import annotations

import re
from typing import List

from ..extractor.section_extractor import ExtractedPage
from .base import BaseDetector, DetectionResult

MARKETING_HINTS = re.compile(
    r"\b(newsletter|news\s*letter|marketing|promotion|promo|email(?:s)?|subscribe|deals|offers|updates|news|mailing\s*list)\b",
    re.I,
)
PAID_ADD_HINTS = re.compile(
    r"[$£€¥₹]\s?\d+|\b\d+\.\d{2}\b|\bwarranty\b|\binsurance\b|\bprotection\b|\bextended\b|\bexpedited\b|\bgift[-_ ]?wrap\b|\binstall(?:ation)?\b|\bdonation\b|\btip\b|\binsure\b",
    re.I,
)
TERMS_HINTS = re.compile(
    r"\b(terms\s+(?:and|&)\s+conditions|i\s+(?:agree|accept)|privacy\s+policy|i\s+am\s+over)\b",
    re.I,
)

SUGGESTED_FIX = (
    "Default opt-in checkboxes (marketing emails, newsletters, paid add-ons) to UNCHECKED. "
    "Make consent and any extra spend an explicit, opt-in action by the user."
)


class PreselectedOptionDetector(BaseDetector):
    pattern_type = "preselected_options"

    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        out: List[DetectionResult] = []
        for cb in page.checkboxes:
            if not cb.checked:
                continue
            label = (cb.label or "").strip()
            if not label:
                out.append(DetectionResult(
                    pattern_type=self.pattern_type,
                    evidence_text=f"unlabeled checkbox name='{cb.name}'",
                    evidence_selector=cb.selector,
                    confidence=0.6,
                    severity="medium",
                    explanation="A pre-checked checkbox has no visible label, which makes silent opt-ins likely.",
                    suggested_fix=SUGGESTED_FIX,
                    method="dom",
                ))
                continue

            paid = bool(PAID_ADD_HINTS.search(label))
            marketing = bool(MARKETING_HINTS.search(label))
            terms_only = bool(TERMS_HINTS.search(label)) and not (paid or marketing)
            if terms_only:
                # Pre-checked T&C is itself questionable but commonly tolerated; skip to keep precision high.
                continue

            if paid:
                out.append(DetectionResult(
                    pattern_type=self.pattern_type,
                    evidence_text=label[:200],
                    evidence_selector=cb.selector,
                    confidence=0.9,
                    severity="high",
                    explanation="A pre-checked option appears to add a paid product or extra cost without explicit consent.",
                    suggested_fix=SUGGESTED_FIX,
                    method="dom",
                ))
            elif marketing:
                out.append(DetectionResult(
                    pattern_type=self.pattern_type,
                    evidence_text=label[:200],
                    evidence_selector=cb.selector,
                    confidence=0.85,
                    severity="medium",
                    explanation="Marketing / email opt-in is pre-checked. Consent should be opt-in, not opt-out.",
                    suggested_fix=SUGGESTED_FIX,
                    method="dom",
                ))
        return out
