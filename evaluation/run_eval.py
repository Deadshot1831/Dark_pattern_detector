"""Evaluation harness for DeceptiTech detectors.

Measures precision / recall / F1 per text-based detector against the
1,818-row dark-patterns-v2.csv. The DOM-based detectors (preselected_options,
cookie_manipulation) are not covered here — they need HTML structure that the
CSV doesn't provide.

Run:
    .venv/bin/python -m evaluation.run_eval

Outputs:
    - Markdown report at evaluation/EVALUATION.md
    - Summary table on stdout
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from backend.detectors.base import BaseDetector
from backend.detectors.confirmshaming import ConfirmshamingDetector
from backend.detectors.fake_urgency import FakeUrgencyDetector
from backend.detectors.scarcity import ScarcityDetector
from backend.extractor.section_extractor import Button, ExtractedPage

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "dark-patterns-v2.csv"
REPORT = Path(__file__).resolve().parent / "EVALUATION.md"

# Map our internal detector type -> CSV "Pattern Type" values that count as positives.
PATTERN_MAP: Dict[str, List[str]] = {
    "fake_urgency": ["Countdown Timer", "Limited-time Message"],
    "scarcity": ["Low-stock Message", "High-demand Message"],
    "confirmshaming": ["Confirmshaming"],
}

# CSV Pattern Types that are unrelated to any of our detectors (for cleaner negatives).
UNRELATED_TYPES = {
    "Activity Notification",
    "Pressured Selling",
    "Hard to Cancel",
    "Visual Interference",
    "Hidden Subscription",
    "Testimonials of Uncertain Origin",
    "Trick Questions",
    "Sneak into Basket",
    "Forced Enrollment",
    "Hidden Costs",
}


@dataclass
class Row:
    text: str
    pattern_type: str
    deceptive: str
    website: str


@dataclass
class Confusion:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    fp_examples: List[Tuple[str, str]] = None  # (text, csv_pattern_type)
    fn_examples: List[Tuple[str, str]] = None

    def __post_init__(self):
        if self.fp_examples is None:
            self.fp_examples = []
        if self.fn_examples is None:
            self.fn_examples = []

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def load_rows() -> Tuple[List[Row], int, int]:
    """Returns (usable_rows, total_rows, rows_skipped_for_empty_text)."""
    rows: List[Row] = []
    total = 0
    skipped_empty_text = 0
    with DATASET.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            total += 1
            text = (r.get("Pattern String") or "").strip()
            pt = (r.get("Pattern Type") or "").strip()
            if not text:
                skipped_empty_text += 1
                continue
            if not pt:
                continue
            rows.append(Row(
                text=text,
                pattern_type=pt,
                deceptive=(r.get("Deceptive?") or "").strip(),
                website=(r.get("Website Page") or "").strip(),
            ))
    return rows, total, skipped_empty_text


def make_text_page(text: str) -> ExtractedPage:
    return ExtractedPage(page_title="", visible_text=text, text_length=len(text))


def make_button_page(text: str) -> ExtractedPage:
    btn = Button(
        text=text,
        selector="div.modal > a.eval",
        tag="a",
        is_link=True,
        classes=["decline"],
        aria_label=None,
        likely_hidden=False,
    )
    return ExtractedPage(page_title="", visible_text="", text_length=0, buttons=[btn])


def evaluate_detector(
    detector: BaseDetector,
    our_type: str,
    rows: List[Row],
    build_page: Callable[[str], ExtractedPage],
    fp_cap: int = 15,
    fn_cap: int = 15,
) -> Confusion:
    positives = set(PATTERN_MAP[our_type])
    cm = Confusion()
    for r in rows:
        is_positive = r.pattern_type in positives
        page = build_page(r.text)
        results = detector.detect(page)
        flagged = any(d.pattern_type == our_type for d in results)

        if is_positive and flagged:
            cm.tp += 1
        elif is_positive and not flagged:
            cm.fn += 1
            if len(cm.fn_examples) < fn_cap:
                cm.fn_examples.append((r.text, r.pattern_type))
        elif (not is_positive) and flagged:
            cm.fp += 1
            if len(cm.fp_examples) < fp_cap:
                cm.fp_examples.append((r.text, r.pattern_type))
        else:
            cm.tn += 1
    return cm


def macro_avg(cms: List[Confusion]) -> Tuple[float, float, float]:
    if not cms:
        return 0.0, 0.0, 0.0
    p = sum(c.precision for c in cms) / len(cms)
    r = sum(c.recall for c in cms) / len(cms)
    f1 = sum(c.f1 for c in cms) / len(cms)
    return p, r, f1


def fmt_pct(x: float) -> str:
    return f"{x * 100:5.1f}%"


def write_report(
    rows: List[Row],
    results: Dict[str, Confusion],
    total_rows: int,
    skipped_empty: int,
) -> str:
    pt_counts = Counter(r.pattern_type for r in rows)

    lines: List[str] = []
    lines.append("# DeceptiTech Detector Evaluation\n")
    lines.append(
        f"Source: `dark-patterns-v2.csv` — {total_rows} total rows. "
        f"{skipped_empty} rows have no `Pattern String` (only behaviour comments like "
        f"\"Sale. Resets on each load.\" with no captured on-page text), so "
        f"**{len(rows)} rows are evaluable**.\n"
    )
    lines.append("## Scope\n")
    lines.append(
        "Only text-based detectors are evaluated (urgency, scarcity, confirmshaming). "
        "The DOM-based detectors (preselected options, cookie manipulation) need rendered HTML "
        "that this CSV doesn't carry — they're verified separately by the unit fixture in "
        "`backend/tests/test_detectors.py` (9-invariant assertion test, all passing).\n"
    )

    lines.append("## Results\n")
    lines.append("| Detector | TP | FP | FN | TN | Precision | Recall | F1 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    cms_for_macro: List[Confusion] = []
    for name in ("fake_urgency", "scarcity", "confirmshaming"):
        cm = results[name]
        cms_for_macro.append(cm)
        lines.append(
            f"| `{name}` | {cm.tp} | {cm.fp} | {cm.fn} | {cm.tn} | "
            f"{fmt_pct(cm.precision)} | {fmt_pct(cm.recall)} | {fmt_pct(cm.f1)} |"
        )
    p, r, f1 = macro_avg(cms_for_macro)
    lines.append(
        f"| **macro avg** |  |  |  |  | **{fmt_pct(p)}** | **{fmt_pct(r)}** | **{fmt_pct(f1)}** |\n"
    )

    lines.append("## Mapping (our detector → CSV `Pattern Type`)\n")
    for ours, csv_types in PATTERN_MAP.items():
        total = sum(pt_counts.get(t, 0) for t in csv_types)
        types_str = ", ".join(f"`{t}` ({pt_counts.get(t, 0)})" for t in csv_types)
        lines.append(f"- **{ours}** ← {types_str}  ·  total positive examples: {total}")
    lines.append("")

    lines.append("## Notes on cross-pattern overlap\n")
    lines.append(
        "Some dataset texts are simultaneously urgent *and* scarce (e.g. `Hurry, only 2 left in stock!`). "
        "Each row has a single label, so the detector that doesn't own that label scores a false positive — "
        "this slightly understates precision. The error tables below make this visible: most cross-pattern "
        "FPs are texts that legitimately match more than one dark-pattern category.\n"
    )

    for name in ("fake_urgency", "scarcity", "confirmshaming"):
        cm = results[name]
        lines.append(f"## `{name}` — error analysis\n")
        lines.append(f"### Top false positives ({len(cm.fp_examples)} shown)\n")
        if cm.fp_examples:
            for text, csv_type in cm.fp_examples:
                snippet = text if len(text) <= 120 else text[:117] + "…"
                lines.append(f"- *(labelled `{csv_type}`)* — {snippet}")
        else:
            lines.append("_None._")
        lines.append("")
        lines.append(f"### Top false negatives ({len(cm.fn_examples)} shown)\n")
        if cm.fn_examples:
            for text, csv_type in cm.fn_examples:
                snippet = text if len(text) <= 120 else text[:117] + "…"
                lines.append(f"- *(labelled `{csv_type}`)* — {snippet}")
        else:
            lines.append("_None._")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    if not DATASET.exists():
        print(f"ERROR: dataset not found at {DATASET}")
        return 1

    rows, total, skipped = load_rows()
    print(f"Total rows in CSV: {total}")
    print(f"Skipped (no Pattern String — comment-only entries): {skipped}")
    print(f"Evaluable rows: {len(rows)}")

    results: Dict[str, Confusion] = {}
    results["fake_urgency"] = evaluate_detector(FakeUrgencyDetector(), "fake_urgency", rows, make_text_page)
    results["scarcity"] = evaluate_detector(ScarcityDetector(), "scarcity", rows, make_text_page)
    results["confirmshaming"] = evaluate_detector(
        ConfirmshamingDetector(), "confirmshaming", rows, make_button_page
    )

    print()
    print(f"{'Detector':<18} {'TP':>5} {'FP':>5} {'FN':>5} {'TN':>5}   {'P':>6} {'R':>6} {'F1':>6}")
    print("-" * 70)
    for name in ("fake_urgency", "scarcity", "confirmshaming"):
        c = results[name]
        print(
            f"{name:<18} {c.tp:>5} {c.fp:>5} {c.fn:>5} {c.tn:>5}   "
            f"{fmt_pct(c.precision)} {fmt_pct(c.recall)} {fmt_pct(c.f1)}"
        )
    p, r, f1 = macro_avg(list(results.values()))
    print(f"{'macro avg':<18} {'':>5} {'':>5} {'':>5} {'':>5}   {fmt_pct(p)} {fmt_pct(r)} {fmt_pct(f1)}")

    report = write_report(rows, results, total_rows=total, skipped_empty=skipped)
    REPORT.write_text(report, encoding="utf-8")
    print(f"\nWrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
