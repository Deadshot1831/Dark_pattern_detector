"""Cookie consent manipulation detection.

Heuristics (in order of strength):
  1. Cookie banner present, Accept button found, Reject button missing       → HIGH
  2. Both present but reject is structurally de-emphasised (anchor with
     secondary/text/link/muted classes, OR text vastly shorter)               → MEDIUM
  3. Cookie banner present but ONLY a 'Manage / Preferences' button beside
     Accept — reject is buried.                                               → MEDIUM
"""
from __future__ import annotations

import re
from typing import List, Optional

from ..extractor.section_extractor import Button, ExtractedPage, Section
from .base import BaseDetector, DetectionResult

ACCEPT_RE = re.compile(r"\b(accept(?:\s+all)?|allow(?:\s+all)?|agree|got\s+it|i\s+accept|ok\s*,?\s*got\s+it)\b", re.I)
REJECT_RE = re.compile(r"\b(reject(?:\s+all)?|decline(?:\s+all)?|deny|refuse|opt\s+out|disable|i\s+decline|do\s+not\s+sell)\b", re.I)
MANAGE_RE = re.compile(r"\b(manage|customi[sz]e|preferences|settings|options|cookie\s+settings|more\s+info)\b", re.I)
DEEMPHASIS_CLASS_RE = re.compile(r"link|text|small|secondary|muted|tertiary|ghost|subtle|underline", re.I)

SUGGESTED_FIX = (
    "Provide an equally prominent 'Reject All' option on the same level as 'Accept All'. "
    "They should match in size, contrast, and position. Don't hide rejection inside a 'Manage Preferences' submenu."
)


def _button_in_banner(btn: Button, banner: Section) -> bool:
    if not btn.selector:
        return False
    if banner.selector and banner.selector in btn.selector:
        return True
    btn_tokens = (btn.selector + " " + " ".join(btn.classes)).lower()
    return bool(re.search(r"cookie|consent|gdpr", btn_tokens))


def _find(buttons: List[Button], pattern: re.Pattern) -> Optional[Button]:
    for b in buttons:
        if pattern.search(b.text or ""):
            return b
    return None


class CookieManipulationDetector(BaseDetector):
    pattern_type = "cookie_manipulation"

    def detect(self, page: ExtractedPage) -> List[DetectionResult]:
        if not page.cookie_banners:
            return []
        banner = page.cookie_banners[0]
        banner_buttons = [b for b in page.buttons if _button_in_banner(b, banner)]
        if not banner_buttons:
            return []

        accept = _find(banner_buttons, ACCEPT_RE)
        reject = _find(banner_buttons, REJECT_RE)
        manage = _find(banner_buttons, MANAGE_RE)

        if not accept:
            # No accept either — probably not a manipulative banner
            return []

        if reject is None:
            evidence = f"Banner has 'Accept' ({accept.text!r}) but no visible 'Reject' option."
            if manage:
                evidence += f" Only 'Manage' ({manage.text!r}) is offered alongside."
            return [DetectionResult(
                pattern_type=self.pattern_type,
                evidence_text=evidence,
                evidence_selector=banner.selector,
                confidence=0.9,
                severity="high",
                explanation="Users have no equivalent way to refuse non-essential cookies — rejection is buried or absent entirely.",
                suggested_fix=SUGGESTED_FIX,
                method="dom",
            )]

        # Both accept and reject exist — check for de-emphasis
        accept_classes = " ".join(accept.classes).lower()
        reject_classes = " ".join(reject.classes).lower()

        reject_is_link = reject.tag == "a" and accept.tag != "a"
        reject_de_emphasised = bool(DEEMPHASIS_CLASS_RE.search(reject_classes)) and not bool(DEEMPHASIS_CLASS_RE.search(accept_classes))
        reject_text_short = len(reject.text or "") + 2 < len(accept.text or "") / 2

        if reject_is_link or reject_de_emphasised or reject_text_short:
            return [DetectionResult(
                pattern_type=self.pattern_type,
                evidence_text=f"Accept: {accept.text!r} ({accept.tag}) vs Reject: {reject.text!r} ({reject.tag})",
                evidence_selector=banner.selector,
                confidence=0.78,
                severity="medium",
                explanation="The 'Reject' option is structurally de-emphasised (different element type, secondary class, or shorter text) compared to 'Accept'.",
                suggested_fix=SUGGESTED_FIX,
                method="dom",
            )]
        return []
