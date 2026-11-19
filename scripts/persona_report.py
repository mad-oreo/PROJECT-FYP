"""Persona report: Component 2 structural-conformance evidence (brief section 11).

Run from the project root:  python scripts/persona_report.py

Writes
  reports/persona_report.md   main table (default config), load-method comparison,
                              G2 factor-method comparison, P04/P05 cliff-edge comparison
  reports/persona_report.csv  main table
  reports/load_method_comparison.csv
  reports/plans/<persona>.json   full plan per persona (default config)
  reports/inputs/<persona>.json  full PlanInputs per persona, for the CLI demo:
                                 python -m components.component2 --input reports/inputs/P03.json --pretty
No timestamps are written, so re-running with unchanged code gives identical files.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.component2 import config, generate_plan  # noqa: E402
from components.component2.models import PlanResult  # noqa: E402
from components.component2.serialize import inputs_to_dict, plan_to_json  # noqa: E402
from personas.loader import all_personas  # noqa: E402

REPORTS = ROOT / "reports"


def _yn(b: bool) -> str:
    return "y" if b else "n"


def _f(x, nd=1) -> str:
    return "" if x is None else f"{x:.{nd}f}"


def count_note(plan: PlanResult, code: str) -> int:
    return sum(1 for w in plan.weeks for s in w.sessions if s.has_note(code))


def main_row(meta: dict, plan: PlanResult) -> dict[str, str]:
    """One report row (brief section 11 columns, plus LONG_RUN_NOT_LONGEST weeks, A-32)."""
    row = {
        "persona": f"{meta['id']} {meta['name']}", "distance": plan.inputs.target_distance,
        "capacity": plan.capacity, "C rule": plan.c_rule, "status": plan.status,
        "start km": _f(plan.inputs.current_weekly_km),
    }
    if plan.status != "OK":
        row.update({"N": "", "hold weeks": "", "warnings": " ".join(m.code for m in plan.warnings)})
        return row
    s = plan.summary
    row.update({
        "N": str(plan.N), "hold weeks": str(plan.hold_weeks),
        "peak km reached": _f(s["peak_km_reached"]), "peak target": _f(s["peak_target_km"], 0),
        "reached target": _yn(s["reached_peak_target"]),
        "G2 fires": str(s["g2_fire_count"]), "G2 weeks": " ".join(s["g2_weeks"]),
        "max ACWR": _f(s["max_acwr"], 3),
        "min easy share": _f(100 * s["min_easy_share"]) + "%",
        "plan easy share (P7)": _f(100 * s["plan_easy_share"]) + "%",
        "max long run km": _f(s["max_long_run_km"]),
        "EASY_RUN_UNDER_30_MIN": str(s["easy_run_under_30_min"]),
        "HARD_SESSION_TOO_SMALL": str(s["hard_session_too_small"]),
        "LONG_RUN_NOT_LONGEST weeks": str(s["long_run_not_longest_weeks"]),
        "avg build increase %": _f(s["avg_build_increase_pct"]),
        "warnings": " ".join(m.code for m in plan.warnings + plan.notes + plan.advisories),
    })
    return row


MAIN_COLS = ["persona", "distance", "capacity", "C rule", "N", "hold weeks", "status", "start km",
             "peak km reached", "peak target", "reached target", "G2 fires", "G2 weeks", "max ACWR",
             "min easy share", "plan easy share (P7)", "max long run km", "EASY_RUN_UNDER_30_MIN",
             "HARD_SESSION_TOO_SMALL", "LONG_RUN_NOT_LONGEST weeks", "avg build increase %", "warnings"]


def md_table(rows: list[dict[str, str]], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def cliff_edge(p04: PlanResult, p05: PlanResult) -> str:
    """P04 (19 km) vs P05 (21 km): same runner either side of the 20 km band edge."""
    cfg = config

    def hard_total(p: PlanResult) -> int:
        return sum(len(w.hard_sessions) for w in p.weeks)

    rows = []
    for label, fn in [
        ("Current km/week", lambda p: _f(p.inputs.current_weekly_km)),
        ("Capacity (rule)", lambda p: f"{p.capacity} ({p.c_rule})"),
        ("Runs per week", lambda p: str(cfg.RUNS_PER_WEEK[p.capacity])),
        ("Hard sessions per build/peak week", lambda p: str(cfg.HARD_SESSIONS_PER_WEEK[p.capacity])),
        ("V2 step (km)", lambda p: _f(cfg.V2_KM_PER_RUN * cfg.RUNS_PER_WEEK[p.capacity])),
        ("Peak target (km)", lambda p: _f(p.summary["peak_target_km"], 0)),
        ("Peak km reached", lambda p: _f(p.summary["peak_km_reached"])),
        ("Total plan km", lambda p: _f(p.summary["plan_km"])),
        ("Hard sessions in plan", lambda p: str(hard_total(p))),
        ("G2 fires (weeks)", lambda p: f"{p.summary['g2_fire_count']} ({' '.join(p.summary['g2_weeks'])})"),
        ("Max ACWR", lambda p: _f(p.summary["max_acwr"], 3)),
        ("Min weekly easy share", lambda p: _f(100 * p.summary["min_easy_share"]) + "%"),
        ("All weeks ACWR <= 1.5", lambda p: _yn(all(w.acwr <= cfg.ACWR_CAP + 1e-9 for w in p.weeks))),
        ("All weeks >= 70% easy", lambda p: _yn(all(w.easy_share >= cfg.MIN_EASY_SHARE - 1e-9 for w in p.weeks))),
        ("LONG_RUN_NOT_LONGEST weeks", lambda p: str(p.summary["long_run_not_longest_weeks"])),
    ]:
        rows.append({"": label, "P04 (19 km)": fn(p04), "P05 (21 km)": fn(p05)})
    return md_table(rows, ["", "P04 (19 km)", "P05 (21 km)"])


def main() -> int:
    (REPORTS / "plans").mkdir(parents=True, exist_ok=True)
    (REPORTS / "inputs").mkdir(parents=True, exist_ok=True)
    personas = all_personas()
    cfg_by_method = {m: config.with_overrides(LOAD_METHOD=m) for m in config.LOAD_METHODS}
    cfg_literal = config.with_overrides(G2_FACTOR_METHOD="literal")

    main_rows, cmp_rows, g2_rows = [], [], []
    plans: dict[str, PlanResult] = {}
    for meta, inputs in personas:
        pid = meta["id"]
        plan = generate_plan(inputs)  # default config
        plans[pid] = plan
        main_rows.append(main_row(meta, plan))
        (REPORTS / "inputs" / f"{pid}.json").write_text(json.dumps(inputs_to_dict(inputs), indent=2) + "\n",
                                                        encoding="utf-8")
        (REPORTS / "plans" / f"{pid}.json").write_text(plan_to_json(plan) + "\n", encoding="utf-8")
        if plan.status != "OK":
            continue
        row = {"persona": pid}
        for m, cfg in cfg_by_method.items():
            s = generate_plan(inputs, cfg).summary
            row[f"G2 fires ({m})"] = str(s["g2_fire_count"])
            row[f"G2 weeks ({m})"] = " ".join(s["g2_weeks"])
            row[f"min easy share ({m})"] = _f(100 * s["min_easy_share"]) + "%"
            row[f"peak km reached ({m})"] = _f(s["peak_km_reached"])
        cmp_rows.append(row)
        lit = generate_plan(inputs, cfg_literal)
        g2_rows.append({
            "persona": pid,
            "G2 fires (bisect)": str(plan.summary["g2_fire_count"]),
            "last-resort conversions (bisect)": str(count_note(plan, "G2_HARD_TO_EASY")),
            "min ACWR of cut weeks (bisect)": _f(min((w.acwr for w in plan.weeks if w.governor["fired"]),
                                                    default=None), 3),
            "G2 fires (literal)": str(lit.summary["g2_fire_count"]),
            "last-resort conversions (literal)": str(count_note(lit, "G2_HARD_TO_EASY")),
            "min ACWR of cut weeks (literal)": _f(min((w.acwr for w in lit.weeks if w.governor["fired"]),
                                                     default=None), 3),
            "peak km reached (bisect / literal)": f"{_f(plan.summary['peak_km_reached'])} / "
                                                  f"{_f(lit.summary['peak_km_reached'])}",
        })

    cmp_cols = ["persona"] + [f"{k} ({m})" for k in ("G2 fires", "G2 weeks", "min easy share", "peak km reached")
                              for m in config.LOAD_METHODS]
    g2_cols = list(g2_rows[0].keys()) if g2_rows else []

    with open(REPORTS / "persona_report.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MAIN_COLS)
        w.writeheader()
        w.writerows(main_rows)
    with open(REPORTS / "load_method_comparison.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cmp_cols)
        w.writeheader()
        w.writerows(cmp_rows)

    md = [
        "# PACU Component 2: persona report",
        "",
        "Generated by `python scripts/persona_report.py`. Structural-conformance evidence for the thesis "
        "and the basis for tuning `components/component2/config.py`.",
        "",
        f"Default config: `LOAD_METHOD = \"{config.LOAD_METHOD}\"`, `G2_FACTOR_METHOD = \"{config.G2_FACTOR_METHOD}\"`. "
        "Predicted times for every persona are filled from its 5K time with Riegel (exponent 1.06).",
        "",
        "## 1. Main table (default config)",
        "",
        md_table(main_rows, MAIN_COLS),
        "",
        "Definitions (A-31): *peak km reached* = highest post-governor week km outside the taper; "
        "*reached target* compares it with the V3 peak target (0.05 km rounding tolerance). "
        "*Plan easy share (P7)* = easy km / total km over plan weeks 1..N (hold weeks excluded). "
        "*Avg build increase %* = mean change in actual km for non-recovery PACU build weeks, each against the "
        "previous non-recovery plan week; compare with the 5-9% weekly-increase benchmark "
        "(attributed to Knopp et al., 2024 in the brief; source row TBC), report only.",
        "",
        "## 2. Load method comparison (S6, A-17)",
        "",
        md_table(cmp_rows, cmp_cols),
        "",
        "## 3. G2 factor method (A-49): bisection (default) vs the brief's literal formula",
        "",
        "Literal = f = 1.5 x chronic / load, repeated up to 10 times, then the A-27 last resort. "
        "Because warm-up and cool-down are never scaled, the literal formula only approaches 1.5 from above, "
        "so it often runs out of iterations and converts hard sessions to easy runs.",
        "",
        md_table(g2_rows, g2_cols),
        "",
        "## 4. Cliff edge: P04 (19 km/week) vs P05 (21 km/week)",
        "",
        "Same runner, same race, either side of the 20 km/week mileage band edge (C2 vs C4).",
        "",
        cliff_edge(plans["P04"], plans["P05"]),
        "",
    ]
    (REPORTS / "persona_report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {REPORTS / 'persona_report.md'} and {len(plans)} plans.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
