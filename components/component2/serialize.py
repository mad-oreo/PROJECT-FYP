"""JSON input/output and the --pretty text table (Section 6).

Rounding happens only here: km to 0.1, minutes to whole numbers, paces as
"m:ss/km", dates as ISO strings.
"""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Optional

from .models import Message, PlanInputs, PlanResult, Segment, Session, Week
from .zones import fmt_pace

DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


def parse_duration(value: Any) -> float:
    """Seconds from a number or an 'h:mm:ss' / 'm:ss' string."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).strip().split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def inputs_from_dict(d: dict[str, Any]) -> PlanInputs:
    """Build PlanInputs from JSON-style data (ISO dates; paces/times as seconds or 'm:ss')."""
    kw: dict[str, Any] = dict(
        target_distance=d["target_distance"],
        predicted_times_s={k: parse_duration(v) for k, v in d["predicted_times_s"].items()},
        easy_pace_s_per_km=parse_duration(d["easy_pace_s_per_km"]),
        current_weekly_km=float(d["current_weekly_km"]),
        recovery_answers=tuple(int(q) for q in d["recovery_answers"]),
        injury_flag=bool(d.get("injury_flag", False)),
        race_date=date.fromisoformat(d["race_date"]),
        long_run_weekday=d.get("long_run_weekday"),
        max_hr=d.get("max_hr"),
        override_entry_minimum=bool(d.get("override_entry_minimum", False)),
    )
    if d.get("start_date"):
        kw["start_date"] = date.fromisoformat(d["start_date"])
    return PlanInputs(**kw)


def inputs_to_dict(inputs: PlanInputs) -> dict[str, Any]:
    return {
        "target_distance": inputs.target_distance,
        "predicted_times_s": {k: round(v, 1) for k, v in inputs.predicted_times_s.items()},
        "easy_pace_s_per_km": inputs.easy_pace_s_per_km,
        "easy_pace": fmt_pace(inputs.easy_pace_s_per_km),
        "current_weekly_km": inputs.current_weekly_km,
        "recovery_answers": list(inputs.recovery_answers),
        "injury_flag": inputs.injury_flag,
        "race_date": inputs.race_date.isoformat(),
        "start_date": inputs.start_date.isoformat(),
        "long_run_weekday": inputs.long_run_weekday,
        "max_hr": inputs.max_hr,
        "override_entry_minimum": inputs.override_entry_minimum,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _km(x: float) -> float:
    return round(x, 1)


def _r(x: Optional[float], nd: int) -> Optional[float]:
    return None if x is None else round(x, nd)


def _msgs(ms: list[Message]) -> list[dict[str, str]]:
    return [{"code": m.code, "message": m.message} for m in ms]


def segment_to_dict(seg: Segment) -> dict[str, Any]:
    return {
        "kind": seg.kind, "km": _km(seg.km), "zone": seg.zone,
        "pace_s_per_km": round(seg.pace_s_per_km), "pace": fmt_pace(seg.pace_s_per_km),
        "minutes": round(seg.minutes),
    }


def session_to_dict(s: Session) -> dict[str, Any]:
    return {
        "date": s.date.isoformat(), "weekday": s.weekday, "day": DAY_NAMES[s.weekday], "slot": s.slot,
        "title": s.title, "main_zone": s.main_zone,
        "segments": [segment_to_dict(seg) for seg in s.segments],
        "reps": s.reps, "rep_length": s.rep_length,
        "km": _km(s.km), "minutes": round(s.minutes), "target_rpe": s.target_rpe, "load": _r(s.load, 1),
        "hr_range": list(s.hr_range) if s.hr_range else None,
        "strides": s.strides, "run_walk_ok": s.run_walk_ok,
        "rule_trace": list(s.rule_trace), "notes": _msgs(s.notes),
    }


def week_to_dict(w: Week) -> dict[str, Any]:
    return {
        "label": w.label, "start_date": w.start_date.isoformat(), "end_date": w.end_date.isoformat(),
        "daniels_phase": w.daniels_phase, "pacu_phase": w.pacu_phase, "week_type": w.week_type,
        "level_km": _km(w.level_km), "km": _km(w.km), "easy_km": _km(w.easy_km),
        "easy_share": round(w.easy_share, 3), "load": round(w.load, 1),
        "chronic_load": round(w.chronic_load, 1), "acwr": round(w.acwr, 3),
        "governor": {"fired": w.governor["fired"], "factor": round(w.governor["factor"], 4),
                     "iterations": w.governor["iterations"]},
        "rule_trace": list(w.rule_trace), "notes": _msgs(w.notes),
        "sessions": [session_to_dict(s) for s in w.sessions],
    }


def _summary_to_dict(summary: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in summary.items():
        if isinstance(v, bool) or v is None or isinstance(v, (int, list, str)):
            out[k] = v
        elif "share" in k or "acwr" in k:
            out[k] = round(v, 3)
        else:
            out[k] = round(v, 1)
    return out


def plan_to_dict(plan: PlanResult) -> dict[str, Any]:
    """Serialize a PlanResult (ISO dates, paces as 'm:ss/km', rounded at output)."""
    cfg = plan.context.cfg if plan.context else None
    race = None
    if plan.race:
        race = dict(plan.race)
        race["date"] = race["date"].isoformat()
        race["pace"] = fmt_pace(race.pop("pace_s_per_km"))
        race["predicted_time_s"] = round(race["predicted_time_s"])
    return {
        "status": plan.status,
        "warnings": _msgs(plan.warnings), "notes": _msgs(plan.notes),
        "advisories": _msgs(plan.advisories), "suggestions": _msgs(plan.suggestions),
        "inputs": inputs_to_dict(plan.inputs),
        "recovery_score": plan.recovery_score, "capacity": plan.capacity, "c_rule": plan.c_rule,
        "track": plan.track, "N": plan.N, "hold_weeks": plan.hold_weeks, "phase_lengths": plan.phase_lengths,
        "config": None if cfg is None else {"LOAD_METHOD": cfg.LOAD_METHOD, "G2_FACTOR_METHOD": cfg.G2_FACTOR_METHOD},
        "race": race,
        "summary": _summary_to_dict(plan.summary),
        "weeks": [week_to_dict(w) for w in plan.weeks],
    }


def plan_to_json(plan: PlanResult, indent: int = 2) -> str:
    return json.dumps(plan_to_dict(plan), indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Pretty text table (demo screenshots)
# ---------------------------------------------------------------------------


def pretty_table(plan: PlanResult) -> str:
    """Week-by-week text view: dates, session titles, km, easy share and ACWR."""
    inp = plan.inputs
    lines = [f"PACU Component 2 plan | {inp.target_distance} | status {plan.status}"]
    if plan.status != "OK":
        lines.append(f"Capacity {plan.capacity} ({plan.c_rule}), recovery score {plan.recovery_score}")
        lines += [f"  ! {m.code}: {m.message}" for m in plan.warnings]
        lines += [f"  > {m.code}: {m.message}" for m in plan.suggestions]
        return "\n".join(lines)
    race = plan.race or {}
    pl = plan.phase_lengths
    lines.append(
        f"Capacity {plan.capacity} ({plan.c_rule}), recovery score {plan.recovery_score}, track {plan.track} | "
        f"N={plan.N} (I/II/III/IV = {pl['I']}/{pl['II']}/{pl['III']}/{pl['IV']}), hold weeks {plan.hold_weeks} | "
        f"race {race.get('date')} predicted {race.get('predicted_time')}"
    )
    for title, msgs in (("Warning", plan.warnings), ("Note", plan.notes), ("Advisory", plan.advisories)):
        lines += [f"  {title} {m.code}: {m.message}" for m in msgs]
    lines.append("")
    lines.append(f"{'Week':<5} {'Dates':<15} {'Phase':<6} {'Type':<9} {'Level':>6} {'km':>6} {'Easy':>5} "
                 f"{'ACWR':>5}  G2")
    for w in plan.weeks:
        g2 = f"x{w.governor['factor']:.2f}" if w.governor["fired"] else ""
        dates = f"{w.start_date:%d %b}-{w.end_date:%d %b}"
        lines.append(f"{w.label:<5} {dates:<15} {w.pacu_phase:<6} {w.week_type:<9} {w.level_km:>6.1f} "
                     f"{w.km:>6.1f} {w.easy_share * 100:>4.0f}% {w.acwr:>5.2f}  {g2}")
        for s in w.sessions:
            lines.append(f"        {DAY_NAMES[s.weekday]} {s.date:%d %b}  {s.slot:<4}  {s.title}")
    s = plan.summary
    lines.append("")
    lines.append(
        f"Peak km reached {s['peak_km_reached']:.1f} / target {s['peak_target_km']:.0f} | G2 fired "
        f"{s['g2_fire_count']}x {s['g2_weeks']} | max ACWR {s['max_acwr']:.2f} | min easy share "
        f"{s['min_easy_share'] * 100:.0f}% | plan easy share {s['plan_easy_share'] * 100:.0f}%"
    )
    return "\n".join(lines)
