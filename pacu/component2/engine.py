"""Section 5 pipeline and the Component 3 hooks (Section 7).

Pipeline: validate -> capacity (C) -> entry check (V4) -> N, hold weeks, dates
(P1, P2, P2b) -> phases (P3) and taper (T1) -> levels (V1-V3, P4, T2) -> for each
week: layout, long run, hard sessions, easy runs, P6, loads, governor -> summary.
"""
from __future__ import annotations

import copy
from typing import Any, Optional

from . import config as default_config
from .capacity import decide_capacity
from .governor import govern_week
from .load import baseline_load
from .models import (
    HARD, HOLD, LONG, RACE_WEEK, RECOVERY, TAPER, Message, PlanContext, PlanInputs, PlanResult, WeekSpec,
)
from .phases import phase_lengths, plan_phases, taper_length
from .plan_calendar import length_messages, plan_calendar
from .sessions import build_week
from .taper import taper_levels
from .volume import below_entry_minimum, entry_suggestions, peak_target_km, weekly_levels
from .zones import build_paces, fmt_pace, fmt_time, predicted_paces

INJURY_ADVISORY = ("Hard sessions are paused while you report an injury or illness. Please see a doctor "
                   "or physiotherapist. They will be added back when your weekly check-in is clear.")


# ---------------------------------------------------------------------------
# Step 1: validation
# ---------------------------------------------------------------------------


def validate(inputs: PlanInputs, cfg: Any) -> list[Message]:
    """Section 3 validation. Raises ValueError for invalid inputs; returns warnings."""
    if inputs.target_distance not in cfg.DISTANCES:
        raise ValueError(f"target_distance must be one of {cfg.DISTANCES}")
    missing = [d for d in cfg.DISTANCES if d not in inputs.predicted_times_s]
    if missing:
        raise ValueError(f"predicted_times_s is missing {missing}")
    if any(inputs.predicted_times_s[d] <= 0 for d in cfg.DISTANCES):
        raise ValueError("predicted times must be positive")
    if inputs.easy_pace_s_per_km <= 0:
        raise ValueError("easy_pace_s_per_km must be positive")
    if inputs.current_weekly_km < 0:
        raise ValueError("current_weekly_km must be >= 0")
    if len(inputs.recovery_answers) != 3 or any(
        not isinstance(q, int) or not cfg.RECOVERY_Q_MIN <= q <= cfg.RECOVERY_Q_MAX for q in inputs.recovery_answers
    ):
        raise ValueError(f"recovery_answers must be three integers {cfg.RECOVERY_Q_MIN}-{cfg.RECOVERY_Q_MAX}")
    if not inputs.race_date > inputs.start_date:
        raise ValueError("race_date must be after start_date")
    if inputs.long_run_weekday is not None and inputs.long_run_weekday not in range(7):
        raise ValueError("long_run_weekday must be 0-6 (Mon=0) or None")
    if inputs.max_hr is not None and inputs.max_hr <= 0:
        raise ValueError("max_hr must be positive")
    warnings = []
    marathon_pace = predicted_paces(inputs.predicted_times_s, cfg)["M"]
    if inputs.easy_pace_s_per_km < marathon_pace:
        warnings.append(Message(
            "EASY_PACE_TOO_FAST",
            f"Easy pace {fmt_pace(inputs.easy_pace_s_per_km)} is faster than the predicted marathon pace "
            f"{fmt_pace(marathon_pace)}; easy runs may be too hard.",
        ))
    return warnings


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def generate_plan(inputs: PlanInputs, cfg: Any = default_config) -> PlanResult:
    """Run the full Component 2 pipeline (Section 5) and return a PlanResult."""
    warnings = validate(inputs, cfg)
    capacity, c_rule, score = decide_capacity(inputs.current_weekly_km, inputs.recovery_answers, cfg)
    distance = inputs.target_distance
    plan = PlanResult(status="OK", inputs=inputs, recovery_score=score, capacity=capacity, c_rule=c_rule,
                      track=cfg.TRACK_OF[distance], warnings=warnings)
    if inputs.injury_flag:
        plan.advisories.append(Message("INJURY_FLAG", INJURY_ADVISORY))  # OWN DESIGN (A-9)

    # V4 entry check. OWN DESIGN (A-11): no plan below the minimum unless overridden
    if below_entry_minimum(distance, inputs.current_weekly_km, cfg):
        if inputs.override_entry_minimum and inputs.current_weekly_km > 0:
            plan.warnings.append(Message(
                "BELOW_ENTRY_MINIMUM",
                f"{inputs.current_weekly_km:g} km/week is below the {cfg.ENTRY_MIN_KM[distance]:g} km/week entry "
                f"minimum for {distance}; plan generated because the override was set (V4, A-11).",
            ))
        else:
            plan.status = "BELOW_ENTRY_MINIMUM"
            plan.suggestions = entry_suggestions(distance, inputs.current_weekly_km, cfg)
            return plan

    # P1, P2, P2b
    cal = plan_calendar(inputs.start_date, inputs.race_date, cfg)
    plan.N, plan.hold_weeks = cal.n_weeks, cal.hold_weeks
    w, n = length_messages(distance, capacity, cal.n_weeks, cfg)
    plan.warnings += w
    plan.notes += n

    # P3, T1, V1-V3, P4, T2
    phases = plan_phases(cal.n_weeks, distance, cfg)
    plan.phase_lengths = phase_lengths(cal.n_weeks, cfg)
    levels, vnotes = weekly_levels(phases, inputs.current_weekly_km, capacity, distance, cfg)
    plan.notes += vnotes
    levels = taper_levels(levels, phases, cfg)

    # OWN DESIGN (A-43): default long-run day = race weekday
    lrw = inputs.long_run_weekday if inputs.long_run_weekday is not None else inputs.race_date.weekday()
    specs = [
        WeekSpec(label=f"H{j}", plan_index=None, start_date=s, end_date=e, daniels_phase=None, pacu_phase="hold",
                 week_type=HOLD, level_km=float(inputs.current_weekly_km), long_run_weekday=lrw,
                 hard_paused=inputs.injury_flag)
        for j, (s, e) in enumerate(cal.hold_dates, start=1)
    ]
    for ph, lvl, (s, e) in zip(phases, levels, cal.week_dates):
        specs.append(WeekSpec(label=str(ph.plan_index), plan_index=ph.plan_index, start_date=s, end_date=e,
                              daniels_phase=ph.daniels_phase, pacu_phase=ph.pacu_phase, week_type=ph.week_type,
                              level_km=lvl, long_run_weekday=lrw, hard_paused=inputs.injury_flag))

    plan.context = PlanContext(
        inputs=inputs, cfg=cfg, distance=distance, track=cfg.TRACK_OF[distance], capacity=capacity,
        paces=build_paces(inputs, cfg), n_weeks=cal.n_weeks, taper_len=taper_length(distance, cal.n_weeks, cfg),
        phase_lengths=plan.phase_lengths, peak_target_km=peak_target_km(distance, capacity, cfg),
    )
    plan.weeks = []
    for i, spec in enumerate(specs):
        week = build_week(spec, plan.context, plan.weeks, specs)
        govern_week(week, load_history(plan, i), cfg)  # G4: the governor runs last
        plan.weeks.append(week)

    p = plan.context.paces
    plan.race = {
        "date": inputs.race_date, "distance": distance, "km": cfg.DISTANCE_KM[distance],
        "predicted_time_s": inputs.predicted_times_s[distance],
        "predicted_time": fmt_time(inputs.predicted_times_s[distance]), "pace_s_per_km": p.race,
        "rule_trace": ["A-7", "A-4"],
    }
    plan.summary = summarize(plan)
    return plan


def load_history(plan: PlanResult, index: int) -> list[float]:
    """G6 + G1: 4 baseline loads, then the actual loads of weeks before ``index``."""
    ctx_cfg = plan.context.cfg
    base = baseline_load(plan.inputs.current_weekly_km, plan.inputs.easy_pace_s_per_km, ctx_cfg)
    return [base] * ctx_cfg.BASELINE_WEEKS + [w.load for w in plan.weeks[:index]]


# ---------------------------------------------------------------------------
# Summary (A-31 definitions)
# ---------------------------------------------------------------------------


def summarize(plan: PlanResult) -> dict[str, Any]:
    """Summary stats. OWN DESIGN (A-31) for the report definitions."""
    cfg = plan.context.cfg
    weeks = plan.weeks
    plan_weeks = [w for w in weeks if w.spec.plan_index is not None]
    non_taper = [w for w in weeks if w.week_type not in (TAPER, RACE_WEEK)]
    sessions = [s for w in weeks for s in w.sessions]
    peak_reached = max(w.km for w in non_taper)
    total_plan_km = sum(w.km for w in plan_weeks)
    total_plan_easy = sum(w.easy_km for w in plan_weeks)

    # Weekly increase in non-recovery build weeks, each vs. the previous non-recovery plan week.
    increases = []
    prev_nonrec: Optional[float] = None
    for w in plan_weeks:
        if w.week_type in (RECOVERY,):
            continue
        if w.pacu_phase == "build" and w.week_type not in (TAPER, RACE_WEEK) and prev_nonrec:
            increases.append(100.0 * (w.km - prev_nonrec) / prev_nonrec)
        prev_nonrec = w.km

    def count(code: str) -> int:
        return sum(1 for s in sessions if s.has_note(code))

    g2 = [w.label for w in weeks if w.governor["fired"]]
    return {
        "weeks_total": len(weeks),
        "plan_km": total_plan_km,
        "start_km": plan.inputs.current_weekly_km,
        "peak_target_km": plan.context.peak_target_km,
        "peak_level_km": max(w.level_km for w in non_taper),
        "peak_km_reached": peak_reached,
        "reached_peak_target": peak_reached >= plan.context.peak_target_km - cfg.REPORT_KM_TOLERANCE,
        "g2_fire_count": len(g2),
        "g2_weeks": g2,
        "max_acwr": max(w.acwr for w in weeks),
        "min_easy_share": min(w.easy_share for w in weeks),
        "plan_easy_share": total_plan_easy / total_plan_km if total_plan_km else 1.0,  # P7, plan weeks only
        "max_long_run_km": max((s.km for s in sessions if s.slot == LONG), default=0.0),
        "hard_sessions": sum(1 for s in sessions if s.slot == HARD),
        "easy_run_under_30_min": count("EASY_RUN_UNDER_30_MIN"),
        "hard_session_too_small": count("HARD_SESSION_TOO_SMALL"),
        "volume_too_low_for_hard": count("VOLUME_TOO_LOW_FOR_HARD"),
        "long_run_not_longest_weeks": sum(1 for w in weeks if w.has_note("LONG_RUN_NOT_LONGEST")),
        "avg_build_increase_pct": sum(increases) / len(increases) if increases else None,
        "build_increase_weeks": len(increases),
    }


# ---------------------------------------------------------------------------
# Component 3 hooks (Section 7). Each returns a new PlanResult.
# ---------------------------------------------------------------------------


def _copy_plan(plan: PlanResult) -> PlanResult:
    if plan.status != "OK" or plan.context is None:
        raise ValueError("Only a generated plan (status OK) can be adjusted.")
    cfg = plan.context.cfg
    return copy.deepcopy(plan, memo={id(cfg): cfg})  # config is shared, not copied


def _rebuild_from(plan: PlanResult, start: int) -> None:
    """Rebuild weeks from ``start`` onward from their specs and re-govern in order."""
    ctx = plan.context
    specs = [w.spec for w in plan.weeks]
    for i in range(start, len(plan.weeks)):
        week = build_week(specs[i], ctx, plan.weeks[:i], specs)
        govern_week(week, load_history(plan, i), ctx.cfg)
        plan.weeks[i] = week
    plan.summary = summarize(plan)


def make_recovery_week(plan: PlanResult, week_label: str) -> PlanResult:
    """P4-style recovery week on demand (Component 3, weekly recovery score Low).

    OWN DESIGN (A-30): level = 80% of the previous week's planned level; later
    weeks keep their levels (G4) but are rebuilt and re-governed in order, so
    earlier G2 cuts can lift. Taper and race weeks are rejected.
    """
    new = _copy_plan(plan)
    i = new.week_index(week_label)
    spec = new.weeks[i].spec
    if spec.week_type in (TAPER, RACE_WEEK):
        raise ValueError(f"Week {week_label} is a {spec.week_type} week; it is already reduced (A-30).")
    prev_level = new.weeks[i - 1].spec.level_km if i > 0 else float(new.inputs.current_weekly_km)
    spec.level_km = new.context.cfg.RECOVERY_WEEK_FRACTION * prev_level
    spec.week_type = RECOVERY
    _rebuild_from(new, i)
    new.notes.append(Message("RECOVERY_WEEK_INSERTED",
                             f"Week {week_label} converted to a recovery week (P4, A-30)."))
    return new


def change_long_run_day(plan: PlanResult, new_weekday: int, from_week_label: str) -> PlanResult:
    """S1 mid-plan change: re-lay weeks from ``from_week_label`` onward, keep volumes,
    re-govern. OWN DESIGN (A-26): S2 conflicts with the previous week are resolved
    in the first re-laid week."""
    if new_weekday not in range(7):
        raise ValueError("new_weekday must be 0-6 (Mon=0)")
    new = _copy_plan(plan)
    i = new.week_index(from_week_label)
    for w in new.weeks[i:]:
        w.spec.long_run_weekday = new_weekday
        w.spec.s2_transition = False
    new.weeks[i].spec.s2_transition = i > 0
    _rebuild_from(new, i)
    new.notes.append(Message("LONG_RUN_DAY_CHANGED",
                             f"Long-run day changed to weekday {new_weekday} from week {from_week_label} (S1)."))
    return new


def clear_injury_flag(plan: PlanResult, from_week_label: str) -> PlanResult:
    """A-9: hard sessions are rebuilt from ``from_week_label`` onward and re-governed in order."""
    new = _copy_plan(plan)
    i = new.week_index(from_week_label)
    for w in new.weeks[i:]:
        w.spec.hard_paused = False
    _rebuild_from(new, i)
    new.advisories = [a for a in new.advisories if a.code != "INJURY_FLAG"]
    new.notes.append(Message("INJURY_CLEARED", f"Hard sessions resume from week {from_week_label} (A-9)."))
    return new
