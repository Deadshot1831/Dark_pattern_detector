"""Prompt builders for each pattern type the LLM helps with."""
from __future__ import annotations

from typing import List, Tuple

# Hand-curated neutral declines — these MUST NOT be flagged by the model.
CONFIRMSHAMING_NEGATIVES: List[str] = [
    "No thanks",
    "Skip",
    "Cancel",
    "Maybe later",
    "Close",
    "Not now",
    "Decline",
    "Dismiss",
    "Not interested",
]


def build_confirmshaming_prompt(text: str, positive_examples: List[str]) -> Tuple[str, str]:
    """Return (system, user) messages for a single button/link classification."""
    pos_block = "\n".join(f"- {e}" for e in positive_examples[:6]) or "- (none)"
    neg_block = "\n".join(f"- {e}" for e in CONFIRMSHAMING_NEGATIVES)

    system = (
        "You are a UX auditor specialising in dark patterns. "
        "Given a single button or link text from a popup, modal, or banner, decide whether the text is "
        "CONFIRMSHAMING — a decline option phrased so it mocks, shames, or guilt-trips the user for declining "
        "(often via self-deprecating phrasing like 'I hate saving money' or 'I'd rather pay retail').\n\n"
        "POSITIVE examples (real confirmshaming text from a labelled dataset):\n"
        f"{pos_block}\n\n"
        "NEGATIVE examples (neutral declines — these are NOT confirmshaming):\n"
        f"{neg_block}\n\n"
        "Rules:\n"
        "1. The text must be self-deprecating, sarcastic, or shame-laden to qualify.\n"
        "2. Plain refusals like 'No thanks', 'Skip', 'Cancel', 'Not now' are NOT confirmshaming.\n"
        "3. If unsure, lean toward false (low confidence).\n\n"
        'Respond ONLY with JSON, exactly this shape: '
        '{"is_confirmshaming": true|false, "confidence": 0.0-1.0, "reason": "<one short sentence>"}'
    )
    user = f"Classify this button/link text:\n\n{text!r}"
    return system, user
