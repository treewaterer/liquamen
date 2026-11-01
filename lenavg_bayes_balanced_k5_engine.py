#!/usr/bin/env python3
"""lenavg_bayes_balanced_k5_engine v1 (2026-10-31): LenAvgBayesL6KEngine with cyclic Latin-square option-order shifts
for choice questions with K >= 5 options (5 <= K <= 52):

  - For K <= 4: uses oavg_engine.random_orders(K, k) unchanged.
  - For 5 <= K <= 52: uses k = 4 cyclic shifts of the engine's base order with evenly spaced steps
    s_j = round(j * K / k) mod K (deduplicated modulo K), so every option rotates uniformly across early,
    middle, and late letter positions across the 4 passes.

    python -m decision_index run --engine lenavg_bayes_balanced_k5_engine:LenAvgBayesBalancedK5Engine --option model=<export> ...
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import lenavg_bayes_l6k_engine as l6k                         # noqa: E402
import oavg_engine as oe                                      # noqa: E402

VERSION = "lenavg_bayes_balanced_k5_engine v1 (2026-10-31)"
_ORIG_RANDOM_ORDERS = oe.random_orders


def balanced_k5_orders(K, k=oe.K_AVG):
    if K <= 4:
        return _ORIG_RANDOM_ORDERS(K, k)
    steps = [int(round(j * K / k)) % K for j in range(k)]
    used = []
    for s in steps:
        while s in used:
            s = (s + 1) % K
        used.append(s)
    return [[(i + s) % K for i in range(K)] for s in used]


oe.random_orders = balanced_k5_orders


class LenAvgBayesBalancedK5Engine(l6k.LenAvgBayesL6KEngine):
    name = "sd31-dikit-lenavg-bayes-balanced-k5"

    def __init__(self, model="", l_star=6000, l_star_noul=6000, **options):
        super().__init__(model=model, l_star=l_star, l_star_noul=l_star_noul, **options)
        self.provenance["lenavg_bayes_balanced_k5_engine"] = VERSION
        self.provenance["lenavg_bayes_balanced_k5_engine_md5"] = hashlib.md5(open(__file__, "rb").read()).hexdigest()
        self.provenance["balanced_k5_orders"] = (
            "Latin-square cyclic shifts steps=[round(j*K/4)%K] for 5<=K<=52; original random_orders for K<=4"
        )
