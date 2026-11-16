"""
Build a fixed 200-row mix:
  - AdvBench: first 100 rows
  - HarmBench: 6 categories × 5 = 30 (equal per category)
  - JailbreakBench: 10 Category × 7 = 70 (equal per category)

Outputs:
  data/comparison_mix_200.csv
  data/comparison_mix_200.meta.json

Seed 42 for reproducibility.
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HARM_PER_CATEGORY = 5
JBB_PER_CATEGORY = 7


def stratified_fixed(
    df: pd.DataFrame, col: str, k: int, random_state: int = 42
) -> pd.DataFrame:
    """Sample exactly ``k`` rows from each distinct value of ``col``."""
    rng = np.random.default_rng(random_state)
    parts: list[pd.DataFrame] = []
    for cat in sorted(df[col].dropna().unique()):
        g = df[df[col] == cat]
        if len(g) < k:
            raise RuntimeError(
                f"stratum {cat!r} needs {k} rows but only {len(g)} available"
            )
        idx = rng.choice(g.index.to_numpy(), size=k, replace=False)
        parts.append(df.loc[idx])
    out = pd.concat(parts, axis=0)
    return out


def main() -> int:
    seed = 42
    adv = pd.read_csv(os.path.join(_REPO, "data", "AdvBench.csv"))
    harm = pd.read_csv(os.path.join(_REPO, "data", "HarmBench.csv"))
    jbb = pd.read_csv(os.path.join(_REPO, "data", "JailbreakBench.csv"))

    n_harm_cat = harm["category"].nunique()
    n_jbb_cat = jbb["Category"].nunique()
    if n_harm_cat != 6:
        raise RuntimeError(f"expected 6 HarmBench categories, got {n_harm_cat}")
    if n_jbb_cat != 10:
        raise RuntimeError(f"expected 10 JailbreakBench categories, got {n_jbb_cat}")

    adv100 = adv.iloc[:100].copy()
    adv100["benchmark"] = "advbench"
    adv100["category"] = ""
    adv100["behavior"] = ""
    adv100["item_source"] = ""
    adv100["orig_index"] = range(len(adv100))

    h30 = stratified_fixed(harm, "category", HARM_PER_CATEGORY, random_state=seed)
    h30 = h30.copy()
    h30["benchmark"] = "harmbench"
    h30["behavior"] = ""
    h30["item_source"] = ""
    h30["orig_index"] = h30.index

    j70 = stratified_fixed(jbb, "Category", JBB_PER_CATEGORY, random_state=seed + 1)
    j70 = j70.copy()
    j70["benchmark"] = "jailbreakbench"
    j70.rename(
        columns={
            "Goal": "goal",
            "Target": "target",
            "Category": "category",
            "Behavior": "behavior",
            "Source": "item_source",
        },
        inplace=True,
    )
    j70["orig_index"] = j70["Index"] if "Index" in j70.columns else j70.index

    cols = ["goal", "target", "benchmark", "category", "behavior", "item_source", "orig_index"]
    for c in cols:
        if c not in adv100.columns:
            adv100[c] = ""
    a = adv100[cols].copy()
    h = h30[cols].copy()
    j = j70[cols].copy()

    mix = pd.concat([a, h, j], axis=0, ignore_index=True)
    mix.insert(0, "mix_id", range(len(mix)))

    out_csv = os.path.join(_REPO, "data", "comparison_mix_200.csv")
    mix.to_csv(out_csv, index=False, encoding="utf-8-sig")

    meta = {
        "seed_harmbench": seed,
        "seed_jailbreakbench": seed + 1,
        "total_rows": len(mix),
        "blocks": [
            {"benchmark": "advbench", "n": len(a), "selection": "first 100 rows of AdvBench.csv"},
            {
                "benchmark": "harmbench",
                "n": len(h),
                "selection": f"{n_harm_cat} categories × {HARM_PER_CATEGORY} = {len(h)}",
                "per_category": h30["category"].value_counts().sort_index().to_dict(),
            },
            {
                "benchmark": "jailbreakbench",
                "n": len(j),
                "selection": f"{n_jbb_cat} categories × {JBB_PER_CATEGORY} = {len(j)}",
                "per_category": j70["category"].value_counts().sort_index().to_dict(),
            },
        ],
        "output_csv": os.path.relpath(out_csv, _REPO),
    }
    out_meta = os.path.join(_REPO, "data", "comparison_mix_200.meta.json")
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Wrote", out_csv)
    print("Wrote", out_meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
