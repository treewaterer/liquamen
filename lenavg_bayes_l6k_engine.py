#!/usr/bin/env python3
"""lenavg_bayes_l6k_engine v1 (2026-10-30): LenAvgBayesEngine with an extended single-question rendered-length gate:

  averaged iff L_raw <= 939 or (len(questions) == 1 and L_rendered <= 6000)

where L_raw = request_length(state, questions) and L_rendered = request_length(render_state(state, "text"), questions).
This brings single-question multiple-choice requests whose rendered text length is at most 6,000 characters inside the
4-order averaging envelope while leaving multi-question or longer requests on the single-pass path.

    python -m decision_index run --engine lenavg_bayes_l6k_engine:LenAvgBayesL6KEngine --option model=<export> ...
"""
from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import garas_core as gc                                       # noqa: E402
import lenavg_bayes_engine as lbe                             # noqa: E402
import lenavg_engine as le                                    # noqa: E402

VERSION = "lenavg_bayes_l6k_engine v1 (2026-10-30)"


class LenAvgBayesL6KEngine(lbe.LenAvgBayesEngine):
    name = "sd31-dikit-lenavg-bayes-l6k"

    def __init__(self, model="", l_star=6000, l_star_noul=6000, **options):
        super().__init__(model=model, l_star=l_star, **options)
        self.l_star_noul = int(l_star_noul)
        self.provenance["lenavg_bayes_l6k_engine"] = VERSION
        self.provenance["lenavg_bayes_l6k_engine_md5"] = hashlib.md5(open(__file__, "rb").read()).hexdigest()
        self.provenance["lenavg_l6k"] = {
            "l_star_choice": self.l_star,
            "l_star_noul": self.l_star_noul,
            "measure": "L_raw <= 939 or (len(questions)==1 and L_rendered <= cutoff)",
        }

    def __call__(self, state, questions):
        L_raw = le.request_length(state, questions)
        st_txt = gc.render_state(state, "text")
        L_ren = le.request_length(st_txt, questions)
        all_noul = bool(questions) and all(q.get("type") == "noul" for q in (questions or {}).values())
        cutoff = self.l_star_noul if all_noul else self.l_star
        self.oavg = self._avg_allowed and (L_raw <= 939 or (len(questions or {}) == 1 and L_ren <= cutoff))
        self.last_choice = {"L_raw": L_raw, "L_ren": L_ren, "all_noul": all_noul, "cutoff": cutoff, "averaged": self.oavg}
        try:
            return super(le.LenAvgEngine, self).__call__(state, questions)
        finally:
            self.oavg = self._avg_allowed
