"""Structured extraction of UI sections relevant to dark pattern detection.

Output is intentionally narrow — only what the 5 MVP detectors need:
  - visible_text       (Fake Urgency, Scarcity)
  - buttons            (Confirmshaming, Cookie Manipulation, Misdirection)
  - checkboxes         (Preselected Options)
  - cookie_banners     (Cookie Manipulation)
  - modals             (Nagging / Confirmshaming context)
  - countdowns         (Fake Urgency)
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from .html_parser import parse, visible_text

COOKIE_HINTS = re.compile(r"cookie|consent|gdpr|privacy[-_ ]?banner", re.I)
MODAL_HINTS = re.compile(r"\b(modal|popup|dialog|overlay|lightbox)\b", re.I)
COUNTDOWN_HINTS = re.compile(r"countdown|count[-_ ]?down|timer|deal[-_ ]?ends", re.I)

HIDDEN_STYLE_RE = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.I)
SNIPPET_LIMIT = 500


@dataclass
class Button:
    text: str
    selector: str
    tag: str
    is_link: bool
    classes: List[str]
    aria_label: Optional[str]
    likely_hidden: bool


@dataclass
class Checkbox:
    label: str
    name: Optional[str]
    value: Optional[str]
    checked: bool
    selector: str


@dataclass
class Section:
    type: str
    text: str
    selector: str
    html_snippet: str


@dataclass
class ExtractedPage:
    page_title: str
    visible_text: str
    text_length: int
    buttons: List[Button] = field(default_factory=list)
    checkboxes: List[Checkbox] = field(default_factory=list)
    cookie_banners: List[Section] = field(default_factory=list)
    modals: List[Section] = field(default_factory=list)
    countdowns: List[Section] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _classes(tag: Tag) -> List[str]:
    raw = tag.get("class")
    if raw is None:
        return []
    if isinstance(raw, str):
        return raw.split()
    return list(raw)


def _selector(tag: Tag, max_depth: int = 4) -> str:
    """Best-effort CSS-ish path. Stops early at an id."""
    parts: List[str] = []
    cur: Optional[Tag] = tag
    while cur is not None and getattr(cur, "name", None) and len(parts) < max_depth:
        node = cur.name
        if cur.get("id"):
            parts.append(f"{node}#{cur['id']}")
            break
        cls = _classes(cur)
        if cls:
            parts.append(f"{node}.{'.'.join(cls[:2])}")
        else:
            parts.append(node)
        cur = cur.parent if isinstance(cur.parent, Tag) else None
    return " > ".join(reversed(parts))


def _likely_hidden(tag: Tag) -> bool:
    style = tag.get("style", "")
    if isinstance(style, list):
        style = " ".join(style)
    if HIDDEN_STYLE_RE.search(style or ""):
        return True
    if tag.get("hidden") is not None:
        return True
    if tag.get("aria-hidden") in ("true", True):
        return True
    return False


def _text_of(tag: Tag, limit: int = 200) -> str:
    txt = " ".join(tag.get_text(separator=" ", strip=True).split())
    return txt[:limit]


def _snippet(tag: Tag) -> str:
    raw = str(tag)
    return raw[:SNIPPET_LIMIT]


def _label_for_input(soup: BeautifulSoup, inp: Tag) -> str:
    # 1. <label for="id">
    inp_id = inp.get("id")
    if inp_id:
        lbl = soup.find("label", attrs={"for": inp_id})
        if lbl:
            return _text_of(lbl)
    # 2. wrapping <label>
    parent = inp.parent
    while parent is not None and getattr(parent, "name", None):
        if parent.name == "label":
            return _text_of(parent)
        parent = parent.parent if isinstance(parent.parent, Tag) else None
    # 3. fall back to aria-label / value / next-sibling text
    for attr in ("aria-label", "title", "value", "placeholder"):
        v = inp.get(attr)
        if v:
            return str(v)
    sib = inp.next_sibling
    while sib is not None:
        if isinstance(sib, str):
            t = sib.strip()
            if t:
                return t[:200]
        elif isinstance(sib, Tag):
            t = _text_of(sib)
            if t:
                return t
        sib = sib.next_sibling
    return ""


def _extract_buttons(soup: BeautifulSoup) -> List[Button]:
    out: List[Button] = []

    for b in soup.find_all("button"):
        out.append(
            Button(
                text=_text_of(b) or (b.get("aria-label") or ""),
                selector=_selector(b),
                tag="button",
                is_link=False,
                classes=_classes(b),
                aria_label=b.get("aria-label"),
                likely_hidden=_likely_hidden(b),
            )
        )

    for inp in soup.find_all("input", attrs={"type": ["submit", "button", "reset"]}):
        text = inp.get("value") or inp.get("aria-label") or ""
        out.append(
            Button(
                text=str(text),
                selector=_selector(inp),
                tag="input",
                is_link=False,
                classes=_classes(inp),
                aria_label=inp.get("aria-label"),
                likely_hidden=_likely_hidden(inp),
            )
        )

    # Anchors that are likely interactive CTAs/decline links:
    #  - role=button or class with btn/button
    #  - class hinting decline/dismiss/skip/close
    #  - short anchor sitting inside a modal/cookie banner ancestor
    for a in soup.find_all("a"):
        text = _text_of(a)
        if not text and not a.get("aria-label"):
            continue
        role = a.get("role")
        cls = _classes(a)
        looks_like_button = role == "button" or any(re.search(r"btn|button", c, re.I) for c in cls)
        dismiss_class = any(DISMISS_CLASS_RE.search(c) for c in cls)
        short_modal_link = len(text) <= 80 and _has_modal_ancestor(a)
        if not (looks_like_button or dismiss_class or short_modal_link):
            continue
        out.append(
            Button(
                text=text or (a.get("aria-label") or ""),
                selector=_selector(a),
                tag="a",
                is_link=True,
                classes=cls,
                aria_label=a.get("aria-label"),
                likely_hidden=_likely_hidden(a),
            )
        )

    return out


def _extract_checkboxes(soup: BeautifulSoup) -> List[Checkbox]:
    out: List[Checkbox] = []
    for inp in soup.find_all("input", attrs={"type": "checkbox"}):
        out.append(
            Checkbox(
                label=_label_for_input(soup, inp),
                name=inp.get("name"),
                value=inp.get("value"),
                checked=inp.has_attr("checked"),
                selector=_selector(inp),
            )
        )
    return out


DISMISS_CLASS_RE = re.compile(r"decline|dismiss|skip|no[-_ ]?thanks|close|cancel", re.I)


def _matches_hint(tag: Tag, pattern: re.Pattern) -> bool:
    tokens = " ".join(_classes(tag) + [tag.get("id") or "", tag.get("role") or ""])
    return bool(pattern.search(tokens))


def _has_modal_ancestor(tag: Tag, depth: int = 6) -> bool:
    cur = tag.parent
    seen = 0
    while cur is not None and isinstance(cur, Tag) and seen < depth:
        if cur.get("role") == "dialog" or _matches_hint(cur, MODAL_HINTS) or _matches_hint(cur, COOKIE_HINTS):
            return True
        cur = cur.parent
        seen += 1
    return False


def _own_text(tag: Tag, limit: int = 200) -> str:
    """Text from this tag's *direct* string children only — excludes descendants."""
    parts = []
    for child in tag.children:
        if isinstance(child, str):
            s = child.strip()
            if s:
                parts.append(s)
    return " ".join(" ".join(parts).split())[:limit]


def _extract_sections(soup: BeautifulSoup) -> tuple[List[Section], List[Section], List[Section]]:
    cookie: List[Section] = []
    modals: List[Section] = []
    countdowns: List[Section] = []

    seen_cookie_ids: set[int] = set()
    seen_modal_ids: set[int] = set()
    seen_countdown_ids: set[int] = set()

    countdown_text_re = re.compile(
        r"\b(\d{1,2}\s*:\s*\d{2}(?:\s*:\s*\d{2})?|ends in|hurry|time left|expires? in|deal ends)\b",
        re.I,
    )
    cookie_text_re = re.compile(r"\bcookies?\b|\bconsent\b|\bgdpr\b", re.I)

    for tag in soup.find_all(True):
        text = _text_of(tag, limit=400)
        if not text and tag.name not in {"div", "section", "aside"}:
            continue

        # Cookie banners — class/id hint, OR a small element directly carrying the phrase
        cookie_class_match = _matches_hint(tag, COOKIE_HINTS)
        cookie_text_match = (
            len(text) < 400
            and len(list(tag.find_all(True))) <= 12
            and bool(cookie_text_re.search(text))
        )
        if cookie_class_match or cookie_text_match:
            if id(tag) not in seen_cookie_ids:
                cookie.append(
                    Section(type="cookie_banner", text=text, selector=_selector(tag), html_snippet=_snippet(tag))
                )
                seen_cookie_ids.add(id(tag))

        if _matches_hint(tag, MODAL_HINTS) or tag.get("role") == "dialog":
            if id(tag) not in seen_modal_ids:
                modals.append(
                    Section(type="modal", text=text, selector=_selector(tag), html_snippet=_snippet(tag))
                )
                seen_modal_ids.add(id(tag))

        # Countdown — class/id hint, OR a *leaf-ish* element whose own text matches a timer phrase.
        # We use _own_text so that <body>/<main> wrappers carrying the countdown's text don't match.
        own = _own_text(tag, limit=200)
        countdown_text_match = (
            len(own) > 0
            and len(own) < 200
            and bool(countdown_text_re.search(own))
        )
        if _matches_hint(tag, COUNTDOWN_HINTS) or countdown_text_match:
            if id(tag) not in seen_countdown_ids:
                countdowns.append(
                    Section(type="countdown", text=text, selector=_selector(tag), html_snippet=_snippet(tag))
                )
                seen_countdown_ids.add(id(tag))

    # Keep extraction tight: detectors don't need every nested div
    return _dedupe_by_text(cookie)[:5], _dedupe_by_text(modals)[:5], _dedupe_by_text(countdowns)[:5]


def _dedupe_by_text(sections: List[Section]) -> List[Section]:
    seen: set[str] = set()
    out: List[Section] = []
    for s in sections:
        key = s.text[:200]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out


def extract(html: str, page_title: str = "") -> ExtractedPage:
    soup = parse(html)
    text = visible_text(soup)
    cookie, modals, countdowns = _extract_sections(soup)
    return ExtractedPage(
        page_title=page_title,
        visible_text=text,
        text_length=len(text),
        buttons=_extract_buttons(soup),
        checkboxes=_extract_checkboxes(soup),
        cookie_banners=cookie,
        modals=modals,
        countdowns=countdowns,
    )
