"""Smoke test for the LLM enrichment.

Skips gracefully when Ollama isn't running. When it is, verifies:
  - A confirmshaming variant the rule regex misses ('I'd rather pay retail') IS flagged.
  - A neutral decline ('No thanks') is NOT flagged.

Run:
    .venv/bin/python -m backend.tests.test_llm_classifier
"""
from __future__ import annotations

import asyncio
import sys

from backend.classifier import ollama_client
from backend.classifier.llm_classifier import enrich
from backend.extractor.section_extractor import Button, ExtractedPage


def _page_with_button(text: str, classes: list[str] | None = None) -> ExtractedPage:
    btn = Button(
        text=text,
        selector="div.modal > a.test-link",
        tag="a",
        is_link=True,
        classes=classes or ["decline-link"],
        aria_label=None,
        likely_hidden=False,
    )
    return ExtractedPage(
        page_title="Test",
        visible_text=text,
        text_length=len(text),
        buttons=[btn],
    )


async def main() -> int:
    if not await ollama_client.is_alive():
        print("Ollama is not reachable — skipping LLM integration test (this is fine).")
        return 0

    failures: list[str] = []

    # Positive: a variant the regex pattern set does NOT cover.
    pos_text = "I'd rather pay retail thanks"
    pos = await enrich(_page_with_button(pos_text), rule_results=[])
    print(f"\n[Positive] '{pos_text}' -> {len(pos)} additions")
    for a in pos:
        print(f"   conf={a.confidence:.2f}  reason={a.explanation}")
    if len(pos) == 0:
        failures.append(f"LLM should have flagged: {pos_text!r}")
    elif pos[0].pattern_type != "confirmshaming":
        failures.append(f"wrong pattern_type for positive: {pos[0].pattern_type}")

    # Negative: a neutral decline that must NOT be flagged.
    neg_text = "No thanks"
    neg = await enrich(_page_with_button(neg_text), rule_results=[])
    print(f"\n[Negative] '{neg_text}' -> {len(neg)} additions")
    for a in neg:
        print(f"   conf={a.confidence:.2f}  reason={a.explanation}")
    if len(neg) > 0:
        failures.append(f"LLM falsely flagged neutral decline: {neg_text!r}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll LLM checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
