"""S1-S7: weekly layout, session content, main-set sizing, easy runs, P6 and race week.

Trace ID "S-CT" = the session content table in brief section 4.7 (by track and
PACU phase). Long-track cells: Daniels (2022), Ch. 16, Table 16.2 [log 31];
short-track cells: OWN DESIGN (A-46).
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any, Iterable, Optional, Sequence

from .load import refresh_totals
from .long_run import long_run_km
from .models import (
    EASY, HARD, HOLD, LONG, NORMAL, RACE, RACE_WEEK, RECOVERY, TAPER,
    MainSet, PlanContext, Segment, Session, Week, WeekSpec, fmt_seconds,
)
from .phases import easy_share_target
from .zones import fmt_pace, fmt_time, hr_range

CONTENT = "S-CT"

# ---------------------------------------------------------------------------
# S1: layout
# ---------------------------------------------------------------------------


def offset_of(d: date, long_run_weekday: int) -> int:
    """S1: offset of a date = (weekday - long-run weekday) mod 7."""
    return (d.weekday() - long_run_weekday) % 7


def week_dates(spec: WeekSpec) -> list[date]:
    return [spec.start_date + timedelta(days=i) for i in range(7)]


def layout_for(spec: WeekSpec, capacity: str, cfg: Any) -> dict[date, Optional[str]]:
    """S1: slot (LONG/HARD/EASY or None = rest) for each date of the week."""
    return {d: cfg.LAYOUT[capacity].get(offset_of(d, spec.long_run_weekday)) for d in week_dates(spec)}


def hard_needed(spec: WeekSpec, ctx: PlanContext) -> int:
    """Number of hard sessions the week calls for (before S7/A-20/G2 conversions).

    A-9: none while the injury flag is active. A-2: none in base. A-18: none in hold
    weeks. P4: none in recovery weeks. A-3/T3: race week has exactly 1; other taper
    weeks keep the capacity's count.
    """
    cfg = ctx.cfg
    if spec.hard_paused:  # OWN DESIGN (A-9)
        return 0
    # OWN DESIGN (A-2, A-18); P4
    if spec.week_type in (HOLD, RECOVERY) or spec.pacu_phase in ("base", "hold"):
        return 0
    if spec.week_type == RACE_WEEK:  # OWN DESIGN (A-3)
        return cfg.RACE_WEEK_HARD_SESSIONS
    return cfg.HARD_SESSIONS_PER_WEEK[ctx.capacity]


# ---------------------------------------------------------------------------
# S2: spacing check
# ---------------------------------------------------------------------------


def s2_violations(sessions: Iterable[Session], cfg: Any) -> list[str]:
    """S2: >= 2 easy/rest days between hard sessions; no hard session the day
    before or after a long run (A-44). Works across week boundaries."""
    ss = sorted(sessions, key=lambda s: s.date)
    hard = [s.date for s in ss if s.slot == HARD]
    longs = {s.date for s in ss if s.slot == LONG}
    out = []
    for h in hard:
        for k in range(1, cfg.S2_LONG_RUN_GAP_DAYS + 1):
            if h - timedelta(days=k) in longs or h + timedelta(days=k) in longs:
                out.append(f"{h}: hard session {k} day(s) from a long run")
    for a, b in zip(hard, hard[1:]):
        if (b - a).days - 1 < cfg.S2_MIN_DAYS_BETWEEN_HARD:
            out.append(f"{a} -> {b}: fewer than {cfg.S2_MIN_DAYS_BETWEEN_HARD} days between hard sessions")
    return out


# ---------------------------------------------------------------------------
# S4 / S5 / S7: caps, warm-up and rep sizing
# ---------------------------------------------------------------------------


def s4_class(zone: str, rep_seconds: float, cfg: Any) -> str:
    """S4 class of a main set. Z5 reps are short (<= 2 min at Z5 pace) or intervals."""
    if zone == "Z5":
        return "Z5_SHORT" if rep_seconds <= cfg.S4_Z5_SHORT_REP_MAX_S else "Z5_INTERVAL"
    return zone


def s4_cap_km(cls: str, week_km: float, pace_s_per_km: float, cfg: Any) -> float:
    """S4 per-session main-set cap in km."""
    if cls == "Z3":
        return min(cfg.S4_Z3_FRACTION * week_km, cfg.S4_Z3_MAX_KM, cfg.S4_Z3_MAX_MIN * 60.0 / pace_s_per_km)
    if cls == "Z4":
        return cfg.S4_Z4_FRACTION * week_km
    if cls == "Z5_INTERVAL":
        return min(cfg.S4_Z5_INTERVAL_FRACTION * week_km, cfg.S4_Z5_INTERVAL_MAX_KM)
    if cls == "Z5_SHORT":
        return min(cfg.S4_Z5_SHORT_FRACTION * week_km, cfg.S4_Z5_SHORT_MAX_KM)
    raise ValueError(f"No S4 cap for class {cls!r}")


def warmup_minutes(week_km: float, cfg: Any) -> float:
    """S5: warm-up and cool-down minutes each. OWN DESIGN (A-13)."""
    return cfg.WARMUP_MIN_LOW if week_km < cfg.WARMUP_THRESHOLD_KM else cfg.WARMUP_MIN_HIGH


def halve_rep(length: float, unit: str, cfg: Any) -> float:
    """S7: halve the rep, round down to 100 m / 30 s, floor 200 m / 1 min. OWN DESIGN (A-45)."""
    step, floor_ = (cfg.S7_ROUND_M, cfg.S7_FLOOR_M) if unit == "m" else (cfg.S7_ROUND_S, cfg.S7_FLOOR_S)
    return max(floor_, math.floor(length / 2.0 / step) * step)


def main_set_allowance(ms: MainSet, cls: str, cfg: Any) -> float:
    """S7: allowance = min(S4 cap, P5 budget per session), also <= the A-21/A-24 target.

    OWN DESIGN (A-48): G2 scales this allowance by the cumulative factor; G3 may
    add an absolute cap so the main set stays within S4 of the actual week km.
    """
    a = min(s4_cap_km(cls, ms.week_km_ref, ms.pace_s_per_km, cfg), ms.budget_km)
    if ms.target_km is not None:
        a = min(a, ms.target_km)
    a *= ms.scale
    if ms.cap_override_km is not None:
        a = min(a, ms.cap_override_km)
    return max(a, 0.0)


def size_main_set(ms: MainSet, cfg: Any) -> bool:
    """S7 (A-5, A-45) for reps; A-25 for continuous runs. Returns False if too small.

    Reps = floor(allowance / rep length), minimum 2. If 2 do not fit, halve the
    rep length until they do (floor 200 m / 1 min). Continuous runs are sized by
    the allowance and must last at least 10 min (A-25).
    """
    if ms.unit == "cont":
        cls = s4_class(ms.zone, math.inf, cfg)
        a = main_set_allowance(ms, cls, cfg)
        ms.s4_class, ms.allowance_km, ms.rep_len, ms.halvings = cls, a, 0.0, 0
        ok = a * ms.pace_s_per_km / 60.0 >= cfg.MIN_CONTINUOUS_MIN - cfg.FLOAT_EPS
        ms.reps = 1 if ok else 0
        return ok
    length, halvings = ms.nominal_len, 0
    while True:
        rep_km = length / 1000.0 if ms.unit == "m" else length / ms.pace_s_per_km
        cls = s4_class(ms.zone, rep_km * ms.pace_s_per_km, cfg)
        a = main_set_allowance(ms, cls, cfg)
        reps = math.floor(a / rep_km + cfg.FLOAT_EPS)
        ms.rep_len, ms.allowance_km, ms.s4_class, ms.halvings = length, a, cls, halvings
        if reps >= cfg.S7_MIN_REPS:
            ms.reps = reps
            return True
        shorter = halve_rep(length, ms.unit, cfg)
        if shorter >= length:
            ms.reps = 0
            return False
        length, halvings = shorter, halvings + 1


# ---------------------------------------------------------------------------
# Session content (content table, A-12, A-14, A-16, A-21 - A-24, A-46)
# ---------------------------------------------------------------------------


def _hard_planned(spec: WeekSpec, ctx: PlanContext) -> bool:
    return hard_needed(spec, ctx) > 0 and spec.week_type != RACE_WEEK


def alternation_index(spec: WeekSpec, ctx: PlanContext, history: Sequence[Week]) -> int:
    """OWN DESIGN (A-23): Conservative alternation counts only earlier weeks in the
    same sequence that call for a hard session. Short track: build weeks.
    Long track: peak weeks and non-race taper weeks (one continuous sequence)."""
    if ctx.track == "short":
        def in_scope(s: WeekSpec) -> bool:
            return s.pacu_phase == "build"
    else:
        def in_scope(s: WeekSpec) -> bool:
            return s.pacu_phase in ("peak", "taper") and s.week_type != RACE_WEEK
    return sum(1 for w in history if w.spec.plan_index is not None and in_scope(w.spec) and _hard_planned(w.spec, ctx))


def _lt_build_code(spec: WeekSpec, ctx: PlanContext, all_specs: Sequence[WeekSpec]) -> str:
    """Long-track build reps. OWN DESIGN (A-24): first floor(B/2) build weeks use 3 min
    reps, the rest 5 min; the last build week with hard sessions gets the 20 min run."""
    build = [s for s in all_specs if s.pacu_phase == "build"]
    hard_build = [s for s in build if hard_needed(s, ctx) > 0]
    if hard_build and hard_build[-1].label == spec.label:
        return "LT_BUILD_LAST"
    pos = [s.label for s in build].index(spec.label) + 1
    return "LT_T_REPS_3MIN" if pos <= len(build) // 2 else "LT_T_REPS_5MIN"


def select_workouts(
    spec: WeekSpec, ctx: PlanContext, n: int, history: Sequence[Week], all_specs: Sequence[WeekSpec]
) -> list[str]:
    """Content table: workout code for Hard #1, Hard #2 (by offset after the long run)."""
    if n == 0:
        return []
    if spec.week_type == RACE_WEEK:
        return ["ST_RACE_WEEK" if ctx.track == "short" else "LT_RACE_WEEK"][:n]
    alt = alternation_index(spec, ctx, history)
    if ctx.track == "short":
        if spec.pacu_phase == "build":
            seq = ["Z4_1K_REPS", "Z3_TEMPO"]  # OWN DESIGN (A-16): Conservative starts with Z4 reps
            return seq[:n] if n >= 2 else [seq[alt % 2]]
        primary, other = (("Z5_400_REPS", "Z4_2K_REPS") if ctx.distance == "5K"
                          else ("Z4_2K_REPS", "Z5_400_REPS"))
        return [primary, other][:n]  # Conservative: primary only
    if spec.pacu_phase == "build":
        return [_lt_build_code(spec, ctx, all_specs)] * n  # Hard #2 repeats Hard #1
    if n >= 2:
        return ["LT_T8_REPS", "LT_RACE_PACE"][:n]
    return [["LT_RACE_PACE", "LT_T8_REPS"][alt % 2]]  # OWN DESIGN (A-16): starts with the race-pace run


def _round_half_up(x: float) -> int:
    return math.floor(x + 0.5)


def last_build_z4_reps(history: Sequence[Week]) -> Optional[int]:
    """OWN DESIGN (A-22): reps of the most recent build week that actually had Z4 1 km reps."""
    for w in reversed(history):
        if w.spec.pacu_phase != "build":
            continue
        for s in w.hard_sessions:
            if s.main_set is not None and s.main_set.workout == "Z4_1K_REPS":
                return s.main_set.reps
    return None


def make_main_set(code: str, ctx: PlanContext, spec: WeekSpec, budget_km: float, history: Sequence[Week]) -> MainSet:
    """Build the main-set template for a workout code (content table)."""
    cfg, p = ctx.cfg, ctx.paces
    lvl = spec.level_km

    def ms(label: str, zone: str, pace: float, unit: str, length: float, jog: float,
           rules: tuple[str, ...], target: Optional[float] = None, workout: str = code) -> MainSet:
        return MainSet(workout=workout, label=label, zone=zone, pace_s_per_km=pace, unit=unit,
                       nominal_len=length, jog_s=jog, budget_km=budget_km, week_km_ref=lvl,
                       rule_ids=rules, target_km=target)

    if code == "Z4_1K_REPS":
        return ms("Threshold reps", "Z4", p.z4, "m", cfg.ST_BUILD_REP_M, cfg.ST_BUILD_JOG_S, ("A-46",))
    if code == "Z3_TEMPO":
        return ms("Tempo run", "Z3", p.z3_tempo, "cont", 0.0, 0.0, ("A-46", "A-12", "A-25"))
    if code == "Z5_400_REPS":
        return ms("Interval reps", "Z5", p.z5, "m", cfg.ST_PEAK_5K_REP_M, cfg.ST_PEAK_5K_JOG_S, ("A-46",))
    if code == "Z4_2K_REPS":
        return ms("Threshold reps", "Z4", p.z4, "m", cfg.ST_PEAK_10K_REP_M, cfg.ST_PEAK_10K_JOG_S, ("A-46", "A-14"))
    if code == "ST_RACE_WEEK":  # OWN DESIGN (A-21, A-22): target reps, then the S4 cap wins
        last = last_build_z4_reps(history)
        reps = cfg.ST_RACE_WEEK_MIN_REPS if last is None else max(cfg.ST_RACE_WEEK_MIN_REPS, _round_half_up(last * cfg.ST_RACE_WEEK_REP_FRACTION))
        return ms("Race-week threshold reps", "Z4", p.z4, "m", cfg.ST_RACE_WEEK_REP_M, cfg.ST_RACE_WEEK_JOG_S,
                  ("A-46", "A-21", "A-22"), target=reps * cfg.ST_RACE_WEEK_REP_M / 1000.0)
    if code == "LT_T_REPS_3MIN":
        return ms("T reps", "Z4", p.z4, "s", cfg.LT_BUILD_REP_S_FIRST_HALF, cfg.LT_BUILD_JOG_S, ("A-24",))
    if code == "LT_T_REPS_5MIN":
        return ms("T reps", "Z4", p.z4, "s", cfg.LT_BUILD_REP_S_SECOND_HALF, cfg.LT_BUILD_JOG_S, ("A-24",))
    if code == "LT_BUILD_LAST":
        cont_km = cfg.LT_BUILD_CONTINUOUS_MIN * 60.0 / p.z4
        allow = min(s4_cap_km("Z4", lvl, p.z4, cfg), budget_km)
        if cont_km <= allow + cfg.FLOAT_EPS:
            return ms("Continuous threshold run", "Z4", p.z4, "cont", 0.0, 0.0, ("A-24", "A-25"),
                      target=cont_km, workout="LT_T_CONTINUOUS")
        return ms("T reps", "Z4", p.z4, "s", cfg.LT_BUILD_REP_S_SECOND_HALF, cfg.LT_BUILD_JOG_S, ("A-24",),
                  workout="LT_T_REPS_5MIN")
    if code == "LT_T8_REPS":
        return ms("T reps", "Z4", p.z4, "s", cfg.LT_PEAK_REP_S, cfg.LT_PEAK_JOG_S, ("A-14",))
    if code == "LT_RACE_PACE":
        return ms("Race-pace run", "Z3", p.z3_race, "cont", 0.0, 0.0, ("A-12", "A-25"))
    if code == "LT_RACE_WEEK":  # OWN DESIGN (A-21): 4 x 5 min is the target; the S4 cap wins
        return ms("Race-week T reps", "Z4", p.z4, "s", cfg.LT_RACE_WEEK_REP_S, cfg.LT_RACE_WEEK_JOG_S, ("A-21",),
                  target=cfg.LT_RACE_WEEK_REPS * cfg.LT_RACE_WEEK_REP_S / p.z4)
    raise ValueError(f"Unknown workout code {code!r}")


# ---------------------------------------------------------------------------
# Session constructors and conversions
# ---------------------------------------------------------------------------


def new_easy(d: date, ctx: PlanContext) -> Session:
    """S3: an easy Z2 run; km is set by split_easy."""
    s = Session(date=d, slot=EASY, main_zone="Z2", segments=[Segment("steady", 0.0, "Z2", ctx.paces.easy)])
    s.add_trace("S1", "S3", "S6")
    return s


def new_long(d: date, spec: WeekSpec, ctx: PlanContext) -> Session:
    """L1-L3: the long run at Z2, as long as L1 and L2 allow (A-15).

    OWN DESIGN (A-10): one steady Z2 segment, no marathon-pace segments in v1.
    """
    km, rule = long_run_km(spec.level_km, ctx.distance, ctx.paces.easy, ctx.cfg)
    s = Session(date=d, slot=LONG, main_zone=ctx.cfg.LONG_RUN_ZONE,
                segments=[Segment("steady", km, ctx.cfg.LONG_RUN_ZONE, ctx.paces.easy)])
    s.add_trace("S1", rule, "L3", "A-15", "A-10", "S6")
    return s


def new_race(d: date, ctx: PlanContext, replaced_slot: Optional[str]) -> Session:
    """A-7: the race on race day at the predicted race pace (excluded from totals, A-4)."""
    km = ctx.cfg.DISTANCE_KM[ctx.distance]
    s = Session(date=d, slot=RACE, main_zone=None, segments=[Segment("steady", km, None, ctx.paces.race)])
    s.add_trace("A-7", "A-4")
    if replaced_slot not in (None, LONG):
        s.add_trace("A-29")
    s.add_note("RACE_EXCLUDED", "The race is excluded from week km, easy share, load and ACWR (A-4).")
    return s


def add_strides(s: Session, n: int, cfg: Any, rule: str) -> None:
    s.strides = n
    s.add_trace(rule)
    s.add_note("STRIDES", f"{n} strides of {cfg.STRIDES_DURATION_TEXT} after the run; "
                          f"their distance is not counted.")


def convert_to_easy(s: Session, ctx: PlanContext, *, strides: int, code: str, message: str,
                    rules: tuple[str, ...]) -> None:
    """Turn a HARD session into an EASY run (km is reassigned by split_easy)."""
    s.slot, s.main_set, s.main_zone, s.warmup_min, s.strides = EASY, None, "Z2", 0.0, 0
    s.segments = [Segment("steady", s.km, "Z2", ctx.paces.easy)]
    s.notes = []  # notes described the hard session; the conversion note replaces them
    s.add_trace(*rules, "S3")
    s.add_note(code, message)
    if strides:
        add_strides(s, strides, ctx.cfg, "A-14")


def rebuild_hard_segments(s: Session, ctx: PlanContext) -> None:
    """S5 + S7: Z1 warm-up, main set (reps with Z1 jogs, or one steady block), Z1 cool-down."""
    p, ms = ctx.paces, s.main_set
    assert ms is not None
    wu_km = s.warmup_min * 60.0 / p.z1
    segs = [Segment("warmup", wu_km, "Z1", p.z1)]
    if ms.unit == "cont":
        segs.append(Segment("steady", ms.allowance_km, ms.zone, ms.pace_s_per_km))
    else:
        jog_km = ms.jog_s / p.z1
        for i in range(ms.reps):
            if i:
                segs.append(Segment("jog", jog_km, "Z1", p.z1))
            segs.append(Segment("rep", ms.rep_km, ms.zone, ms.pace_s_per_km))
    segs.append(Segment("cooldown", wu_km, "Z1", p.z1))
    s.segments = segs


def split_easy(week: Week, target_km: float, ctx: PlanContext) -> float:
    """S3: km left after the long run and hard sessions, split evenly over EASY runs (Z2)."""
    easy = [s for s in week.sessions if s.slot == EASY]
    fixed = sum(s.km for s in week.sessions if s.slot in (LONG, HARD))
    if not easy:
        return 0.0
    per = (target_km - fixed) / len(easy)
    for s in easy:
        s.segments = [Segment("steady", max(per, 0.0), "Z2", ctx.paces.easy)]
    return per


# ---------------------------------------------------------------------------
# P6, titles, notes
# ---------------------------------------------------------------------------


def enforce_p6(week: Week, target_km: float, cfg: Any) -> None:
    """P6: easy km >= 70% of week km; if not, reduce reps (then convert) until it holds."""
    ctx = week.ctx
    refresh_totals(week, cfg)
    while week.easy_share < cfg.MIN_EASY_SHARE - cfg.FLOAT_EPS:
        reducible = [s for s in week.hard_sessions
                     if s.main_set.unit != "cont" and s.main_set.reps > cfg.S7_MIN_REPS]
        if reducible:
            s = max(reducible, key=lambda x: x.main_set.main_km)
            ms = s.main_set
            ms.cap_override_km = (ms.reps - 1) * ms.rep_km
            size_main_set(ms, cfg)
            rebuild_hard_segments(s, ctx)
            s.add_trace("P6")
            s.add_note("P6_REPS_REDUCED", "Reps reduced so the week stays at least 70% easy (P6).")
        elif week.hard_sessions:
            s = max(week.hard_sessions, key=lambda x: x.date)
            convert_to_easy(s, ctx, strides=0, code="P6_HARD_TO_EASY",
                            message="Hard session made easy so the week stays at least 70% easy (P6).",
                            rules=("P6",))
        else:
            break
        split_easy(week, target_km, ctx)
        refresh_totals(week, cfg)
    week.add_trace("P6")


def session_title(s: Session, ctx: PlanContext) -> str:
    """Human-readable title, e.g. '6 x 400 m @ 5:42/km, 90 s jog'."""
    p = ctx.paces
    if s.slot == RACE:
        t = ctx.inputs.predicted_times_s[ctx.distance]
        return f"RACE {ctx.distance}: {s.km:.1f} km @ {fmt_pace(p.race)} (predicted {fmt_time(t)})"
    if s.slot == LONG:
        return f"Long run {s.km:.1f} km @ {fmt_pace(p.easy)}"
    if s.slot == EASY:
        t = f"Easy {s.km:.1f} km @ {fmt_pace(p.easy)}"
        if s.strides:
            t += f" + {s.strides} strides"
        if s.run_walk_ok:
            t += " (run/walk OK)"
        return t
    ms = s.main_set
    assert ms is not None
    if ms.unit == "cont":
        mins = ms.allowance_km * ms.pace_s_per_km / 60.0
        t = f"{ms.label} {mins:.0f} min ({ms.allowance_km:.1f} km) @ {fmt_pace(ms.pace_s_per_km)}"
    else:
        rep = f"{ms.rep_len:.0f} m" if ms.unit == "m" else fmt_seconds(ms.rep_len)
        t = f"{ms.reps} × {rep} @ {fmt_pace(ms.pace_s_per_km)}, {fmt_seconds(ms.jog_s)} jog"
    if s.strides:
        t += f" + {s.strides} strides"
    return t


def refresh_week(week: Week, cfg: Any) -> None:
    """Titles, HR ranges, loads (S6), week totals and the S3 / A-32 notes."""
    ctx = week.ctx
    for s in week.sessions:
        s.title = session_title(s, ctx)
        s.hr_range = hr_range(s.main_zone, ctx.inputs.max_hr, cfg)
        if s.slot == EASY:
            s.notes = [n for n in s.notes if n.code != "EASY_RUN_UNDER_30_MIN"]
            if s.minutes < cfg.EASY_RUN_MIN_MIN - cfg.FLOAT_EPS:
                s.add_note("EASY_RUN_UNDER_30_MIN",
                           f"Easy run is {s.minutes:.0f} min; aim for at least {cfg.EASY_RUN_MIN_MIN:.0f} min (S3). "
                           f"Volume is not changed.")
    refresh_totals(week, cfg)
    # OWN DESIGN (A-32): flag weeks where an easy run is longer than the long run
    week.notes = [n for n in week.notes if n.code != "LONG_RUN_NOT_LONGEST"]
    longs = [s for s in week.sessions if s.slot == LONG]
    if longs and any(s.km > longs[0].km + cfg.FLOAT_EPS for s in week.sessions if s.slot == EASY):
        week.add_note("LONG_RUN_NOT_LONGEST",
                      "An easy run is longer than the long run this week (only easy runs are compared). (A-32)")
        week.add_trace("A-32")


# ---------------------------------------------------------------------------
# Week assembly (pipeline steps 7.1 - 7.6)
# ---------------------------------------------------------------------------


def week_type_rules(spec: WeekSpec, ctx: PlanContext) -> tuple[str, ...]:
    """Rule IDs that set this week's type and level."""
    if spec.week_type == HOLD:
        return ("P1", "A-18")
    base = ("P1", "P3", "A-1")
    if spec.week_type == RECOVERY:
        return base + ("P4", "A-40")
    if spec.week_type == TAPER:
        return base + ("T1", "T2", "T3", "A-8", "A-39")
    if spec.week_type == RACE_WEEK:
        return base + ("T1", "T2", "T3", "A-3", "A-7", "A-4")
    rules = base + (("V1",) if spec.plan_index == 1 else ("V2",))
    if spec.level_km >= ctx.peak_target_km - ctx.cfg.FLOAT_EPS:
        rules += ("V3",)
        if ctx.inputs.current_weekly_km >= ctx.peak_target_km:
            rules += ("A-6",)
    return rules


def _apply_s2_transition(week: Week, prev: Week, ctx: PlanContext) -> None:
    """OWN DESIGN (A-26): in the first week after a long-run day change, any HARD
    session that breaks S2 against the previous week becomes EASY + strides."""
    cfg = ctx.cfg
    prev_hard = [s.date for s in prev.sessions if s.slot == HARD]
    longs = [s.date for s in prev.sessions + week.sessions if s.slot == LONG]
    for s in sorted(week.hard_sessions, key=lambda x: x.date):
        near_long = any(0 < abs((s.date - d).days) <= cfg.S2_LONG_RUN_GAP_DAYS for d in longs)
        near_hard = any(0 < (s.date - h).days <= cfg.S2_MIN_DAYS_BETWEEN_HARD for h in prev_hard)
        if near_long or near_hard:
            convert_to_easy(s, ctx, strides=cfg.STRIDES_COUNT, code="S2_TRANSITION",
                            message="Made easy: the long-run day changed and this hard session would break "
                                    "S2 spacing with last week (A-26).", rules=("S2", "A-26"))
    this_long = [s.date for s in week.sessions if s.slot == LONG]
    if any(0 < (d - h).days <= cfg.S2_LONG_RUN_GAP_DAYS for d in this_long for h in prev_hard):
        week.add_note("S2_TRANSITION_UNRESOLVED",
                      "Last week's hard session falls the day before this week's long run after the "
                      "long-run day change; it was already scheduled, so it is left as is (A-26).")


def build_week(spec: WeekSpec, ctx: PlanContext, history: Sequence[Week], all_specs: Sequence[WeekSpec]) -> Week:
    """Pipeline step 7.1-7.6 for one week: layout, long run, hard sessions, easy
    runs, P6 and loads. The governor (7.7) runs separately."""
    cfg = ctx.cfg
    week = Week(spec=spec, ctx=ctx)
    week.add_trace(*week_type_rules(spec, ctx))
    if spec.hard_paused:
        week.add_trace("A-9")
    days = week_dates(spec)
    layout = layout_for(spec, ctx.capacity, cfg)
    week.add_trace("S1", "S2")

    is_race = spec.week_type == RACE_WEEK
    replaced: Optional[str] = None
    race_day = ctx.inputs.race_date
    if is_race:
        if race_day not in days:
            raise ValueError("Race week does not contain race day (A-7).")
        replaced = layout[race_day]
        if replaced != LONG:
            for d in days:
                if layout[d] == LONG:
                    layout[d] = EASY  # A-7: no long run when its weekday != race weekday
        layout[race_day] = RACE  # OWN DESIGN (A-7, A-29): the race replaces whatever slot is on race day

    hard_days = sorted((d for d in days if layout[d] == HARD), key=lambda d: offset_of(d, spec.long_run_weekday))
    n_hard = hard_needed(spec, ctx)
    if is_race:
        # A-7: 4-6 days before the race, preferring 5; none in the last 3 days.
        cands = [d for d in hard_days if (race_day - d).days in cfg.RACE_WEEK_HARD_DAYS_BEFORE]
        cands.sort(key=lambda d: (abs((race_day - d).days - cfg.RACE_WEEK_HARD_PREFERRED_DAYS_BEFORE),
                                  (race_day - d).days))
        keep = cands[:n_hard]
        if n_hard and not keep:
            week.add_note("RACE_WEEK_NO_HARD_SLOT", "No HARD slot falls 4-6 days before the race, "
                                                    "so race week has no hard session (A-7).")
    else:
        keep = hard_days[:n_hard]  # S1: keep the earliest slots after the long run

    long_track_conservative_base = (ctx.track == "long" and ctx.capacity == "Conservative"
                                    and spec.pacu_phase == "base")
    for d in days:
        slot = layout[d]
        if slot is None:
            continue
        if slot == RACE:
            week.sessions.append(new_race(d, ctx, replaced))
        elif slot == LONG:
            week.sessions.append(new_long(d, spec, ctx))
        elif slot == HARD and d in keep:
            week.sessions.append(Session(date=d, slot=HARD))
        else:
            s = new_easy(d, ctx)
            if slot == HARD:  # a HARD slot that becomes an easy run
                if spec.hard_paused:
                    s.add_trace("A-9")
                    s.add_note("HARD_PAUSED_INJURY", "Hard session paused while an injury or illness "
                                                     "is reported (A-9).")
                elif spec.week_type == HOLD:
                    s.add_trace("A-18")
                elif spec.pacu_phase == "base":
                    s.add_trace("A-2")
                elif spec.week_type == RECOVERY:
                    s.add_trace("P4")
                elif is_race:
                    s.add_trace("A-7")
                if spec.pacu_phase in ("base", "hold"):
                    add_strides(s, cfg.STRIDES_COUNT, cfg, "A-14")
            if long_track_conservative_base:
                s.run_walk_ok = True
                s.add_trace(CONTENT)
            week.sessions.append(s)

    # Hard sessions: content table, P5 budget, S4/S5/S7
    hards = sorted(week.hard_sessions, key=lambda s: offset_of(s.date, spec.long_run_weekday))
    codes = select_workouts(spec, ctx, len(hards), history, all_specs)
    if hards:
        target = easy_share_target(spec.daniels_phase, cfg)
        budget = (1.0 - target) * spec.level_km / len(hards)  # P5; OWN DESIGN (A-19): split evenly
        wu = warmup_minutes(spec.level_km, cfg)
        for i, (s, code) in enumerate(zip(hards, codes), start=1):
            ms = make_main_set(code, ctx, spec, budget, history)
            s.main_set, s.main_zone, s.warmup_min = ms, ms.zone, wu
            s.add_trace("S1", "S2", f"{CONTENT}({ctx.track},{spec.pacu_phase},#{i})", "P5", "A-19",
                        "S4", "S5", "A-13", "S7", "S6", *ms.rule_ids)
            if code in ("LT_T_REPS_3MIN", "LT_T_REPS_5MIN", "LT_BUILD_LAST"):
                s.strides = cfg.LT_BUILD_STRIDES
                s.add_note("STRIDES", f"Plus {cfg.LT_BUILD_STRIDES} strides ({CONTENT}, long-track build).")
            if size_main_set(ms, cfg):
                rebuild_hard_segments(s, ctx)
            else:
                rule = ("A-25",) if ms.unit == "cont" else ("S7", "A-5")
                convert_to_easy(s, ctx, strides=cfg.STRIDES_COUNT, code="HARD_SESSION_TOO_SMALL",
                                message=f"{ms.label} does not fit this week's allowance "
                                        f"({'under 10 min' if ms.unit == 'cont' else 'fewer than 2 reps'}); "
                                        f"easy run with strides instead.", rules=rule)

    if spec.s2_transition and history:
        _apply_s2_transition(week, history[-1], ctx)

    # S3 easy runs, with A-20
    while True:
        per = split_easy(week, spec.level_km, ctx)
        if per >= cfg.EASY_RUN_MIN_KM_FOR_HARD - cfg.FLOAT_EPS or not week.hard_sessions:
            break
        last = max(week.hard_sessions, key=lambda s: s.date)
        convert_to_easy(last, ctx, strides=cfg.STRIDES_COUNT, code="VOLUME_TOO_LOW_FOR_HARD",
                        message="Too little volume left for the easy runs; the last hard session "
                                "becomes an easy run with strides (A-20).", rules=("S3", "A-20"))
    if per < 0:
        raise ValueError(f"Week {spec.label}: long run and hard sessions exceed the week volume.")
    for s in week.sessions:
        if s.slot == LONG:
            week.add_trace(*(r for r in s.rule_trace if r in ("L1", "L2")), "L3")
    if hards:
        week.add_trace("P5", "S4", "S5", "S7")
    week.add_trace("S3")

    enforce_p6(week, spec.level_km, cfg)
    refresh_week(week, cfg)
    week.add_trace("S6")
    return week
