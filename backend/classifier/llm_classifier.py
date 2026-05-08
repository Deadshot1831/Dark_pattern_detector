"""LLM-based detection enrichment.

Strategy: rules run first; this module *adds* findings that the rules missed.
Currently scoped to confirmshaming (the dataset shows extreme variant phrasing
that regex can't capture cleanly). DOM-based detectors (preselected, cookie)
need no LLM input. Urgency/scarcity rules already cover the dataset well.
"""
from __future__ import annotations

import logging
from typing import List

from ..detectors.base import DetectionResult
from ..extractor.section_extractor import Button, ExtractedPage
from . import cache, ollama_client
from .few_shot import load_examples
from .prompts import build_confirmshaming_prompt

log = logging.getLogger(__name__)

SUGGESTED_FIX = (
    "Use neutral, respectful decline copy: 'No thanks', 'Maybe later', 'Skip'. "
    "Avoid wording that mocks, guilt-trips, or shames the user for declining."
)

DECLINE_KEYWORDS = ("no", "skip", "thanks", "later", "decline", "cancel", "close",
                    "i'd", "i prefer", "i'll", "rather", "don't", "hate")


def _is_decline_candidate(btn: Button) -> bool:
    """Cheap pre-filter so we only spend LLM time on plausibly relevant texts."""
    text = (btn.text or "").strip()
    if not text or len(text) > 200:
        return False
    if btn.is_link:  # extractor already filtered to interesting anchors
        return True
    lo = text.lower()
    return len(text) < 100 and any(k in lo for k in DECLINE_KEYWORDS)


async def enrich(
    page: ExtractedPage, rule_results: List[DetectionResult]
) -> List[DetectionResult]:
    """Return DetectionResult objects the rule pass missed.

    No-op (returns []) when Ollama is not reachable or the model is not loaded.
    """
    if not await ollama_client.is_alive():
        log.info("Ollama not available — skipping LLM enrichment")
        return []

    examples = load_examples().get("confirmshaming", [])
    already_flagged = {
        d.evidence_text.strip().lower()
        for d in rule_results
        if d.pattern_type == "confirmshaming"
    }

    additions: List[DetectionResult] = []
    seen_texts: set[str] = set()
    for btn in page.buttons:
        text = (btn.text or "").strip()
        if not text:
            continue
        key = text.lower()
        if key in already_flagged or key in seen_texts:
            continue
        if not _is_decline_candidate(btn):
            continue
        seen_texts.add(key)

        system, user = build_confirmshaming_prompt(text, examples)
        prompt_key = f"{system}\n---\n{user}"

        result = cache.get(prompt_key)
        if result is None:
            result = await ollama_client.chat_json(system, user)
            if result is None:
                continue
            cache.put(prompt_key, result)

        if not isinstance(result, dict):
            continue
        is_flagged = bool(result.get("is_confirmshaming"))
        try:
            confidence = float(result.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0.0

        if is_flagged and confidence >= 0.7:
            additions.append(DetectionResult(
                pattern_type="confirmshaming",
                evidence_text=text,
                evidence_selector=btn.selector,
                confidence=min(confidence, 0.99),
                severity="medium",
                explanation=str(result.get("reason", "Classifier flagged decline as confirmshaming.")) + " (LLM)",
                suggested_fix=SUGGESTED_FIX,
                method="llm",
            ))
    return additions
