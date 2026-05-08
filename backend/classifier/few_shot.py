"""Few-shot example loader.

Reads dark-patterns-v2.csv once, samples a handful of high-quality examples
per pattern type, returns them for embedding into prompts. Sampling is
deterministic (fixed seed) so cached prompts stay valid across runs.
"""
from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "dark-patterns-v2.csv"

# Map our internal detector type to the dataset's "Pattern Type" column values
CSV_TYPE_MAP: Dict[str, List[str]] = {
    "confirmshaming": ["Confirmshaming"],
    "fake_urgency": ["Countdown Timer", "Limited-time Message"],
    "scarcity": ["Low-stock Message", "High-demand Message"],
}

_cache: Dict[str, List[str]] | None = None


def load_examples(n_per_pattern: int = 6) -> Dict[str, List[str]]:
    global _cache
    if _cache is not None:
        return _cache
    if not DATASET_PATH.exists():
        _cache = {}
        return _cache

    by_csv_type: Dict[str, List[str]] = defaultdict(list)
    with DATASET_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s = (row.get("Pattern String") or "").strip()
            t = row.get("Pattern Type", "")
            if s and t and len(s) <= 200:
                by_csv_type[t].append(s)

    rng = random.Random(42)
    out: Dict[str, List[str]] = {}
    for our_type, csv_types in CSV_TYPE_MAP.items():
        pool = []
        for ct in csv_types:
            pool.extend(by_csv_type.get(ct, []))
        if pool:
            out[our_type] = rng.sample(pool, min(n_per_pattern, len(pool)))
    _cache = out
    return _cache
