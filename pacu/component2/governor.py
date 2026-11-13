"""G1-G6: the ACWR safety governor.

G1: ACWR = week load / mean of the previous 4 weeks' actual loads.
G2: if ACWR > 1.5, scale the week by f = 1.5 x chronic / load, repeat up to
    10 times, then convert hard sessions to easy as a last resort (A-27).
G3: after any cut, re-check P6 and L2. OWN DESIGN (A-48): also re-check L1 and
    S4 against the actual (cut) week km, so every cap holds on what is run.
G4: runs last for each week; trims only that week (future V2 levels unchanged).
G6: cold start baseline weeks are supplied by the caller (engine).
"""
from __future__ import annotations

from typing import Any, Sequence

from .load import refresh_totals
from .long_run import l1_cap_km, l2_cap_km
from .models import EASY, HARD, LONG, Week
from .sessions import (
    convert_to_easy, enforce_p6, rebuild_hard_segments, refresh_week, s4_cap_km, size_main_set, split_easy,
)


def chronic_load(previous_loads: Sequence[float], cfg: Any) -> float:
    """G1: mean of the previous 4 weeks' actual loads (baseline weeks fill gaps, G6)."""
    n = cfg.CHRONIC_WINDOW_WEEKS
    if len(previous_loads) < n:
        raise ValueError(f"G1 needs {n} previous loads (pad with G6 baseline loads); got {len(previous_loads)}.")
    chronic = sum(previous_loads[-n:]) / n
    if chronic <= 0:
        raise ValueError("Chronic load is 0; ACWR is undefined (G1).")
    return chronic


def _scale_week(week: Week, f: float, cfg: Any) -> None:
    """G2: scale easy and long-run distances and hard main sets by f (warm-up and
    cool-down unchanged), then recompute reps with S7 (A-48: the allowance is scaled)."""
    ctx = week.ctx
    converted: list[tuple] = []
    for s in week.sessions:
        if s.slot in (LONG, EASY):
            for seg in s.segments:
                seg.km *= f
        elif s.slot == HARD:
            ms = s.main_set
            km_after = s.km * f
            ms.scale *= f
            if size_main_set(ms, cfg):
                rebuild_hard_segments(s, ctx)
            else:
                converted.append((s, km_after, ms.unit))
    if converted:
        target = sum(s.km for s in week.runs if all(s is not c[0] for c in converted))
        target += sum(km for _, km, _ in converted)
        for s, _, unit in converted:
            convert_to_easy(s, ctx, strides=cfg.STRIDES_COUNT, code="HARD_SESSION_TOO_SMALL",
                            message="After the G2 cut the main set no longer fits; easy run with strides instead.",
                            rules=("G2", "A-25") if unit == "cont" else ("G2", "S7", "A-5"))
        split_easy(week, target, ctx)


def _convert_latest_hard(week: Week, cfg: Any) -> None:
    """OWN DESIGN (A-27): last resort, convert the latest hard session to easy; its km
    rejoins the S3 split."""
    target = week.km
    s = max(week.hard_sessions, key=lambda x: x.date)
    convert_to_easy(s, week.ctx, strides=0, code="G2_HARD_TO_EASY",
                    message="Converted to an easy run: scaling alone could not bring ACWR to 1.5 (G2, A-27).",
                    rules=("G2", "A-27"))
    split_easy(week, target, week.ctx)


def _g3_s4(week: Week, cfg: Any) -> None:
    """A-48: every main set within its S4 cap of the actual week km (load can only fall)."""
    ctx = week.ctx
    for _ in range(cfg.G2_MAX_ITERATIONS):
        changed = False
        for s in list(week.hard_sessions):
            ms = s.main_set
            cap = s4_cap_km(ms.s4_class, week.km, ms.pace_s_per_km, cfg)
            if ms.main_km > cap + cfg.FLOAT_EPS:
                ms.cap_override_km = cap
                s.add_trace("G3", "S4")
                if size_main_set(ms, cfg):
                    rebuild_hard_segments(s, ctx)
                else:
                    convert_to_easy(s, ctx, strides=cfg.STRIDES_COUNT, code="HARD_SESSION_TOO_SMALL",
                                    message="After the G2 cut the main set no longer fits S4; easy run with "
                                            "strides instead.", rules=("G3", "S4", "S7", "A-5"))
                changed = True
        refresh_totals(week, cfg)
        if not changed:
            return


def _g3_long_run(week: Week, cfg: Any) -> None:
    """G3: long run within L2 (and L1, A-48) of the actual week km; excess moves to the
    easy runs, which keeps week km and load unchanged (both are Z2)."""
    ctx = week.ctx
    for s in week.sessions:
        if s.slot != LONG:
            continue
        cap = min(l1_cap_km(week.km, ctx.paces.easy, cfg), l2_cap_km(ctx.distance, ctx.paces.easy, cfg))
        if s.km > cap + cfg.FLOAT_EPS:
            easy = [e for e in week.sessions if e.slot == EASY]
            if not easy:
                continue
            excess = s.km - cap
            s.segments[0].km = cap
            for e in easy:
                e.segments[0].km += excess / len(easy)
            s.add_trace("G3")
            s.add_note("G3_LONG_RUN_TRIMMED", "Long run trimmed to stay within L1/L2 of the cut week; "
                                              "the difference moved to the easy runs (G3).")


def govern_week(week: Week, previous_loads: Sequence[float], config: Any) -> Week:
    """G1-G3 on a single week (G5: Component 3's targets must pass through this).

    previous_loads: earlier weeks' actual loads, oldest first, padded at the front
    with G6 baseline loads so at least 4 are present. Modifies and returns ``week``.
    """
    cfg = config
    chronic = chronic_load(previous_loads, cfg)
    refresh_week(week, cfg)
    week.chronic_load = chronic
    week.governor = {"fired": False, "factor": 1.0, "iterations": 0}
    week.add_trace("G1", "G4")
    cap, tol = cfg.ACWR_CAP, cfg.ACWR_TOLERANCE

    def over() -> bool:
        return week.load / chronic > cap + tol

    if not over():
        week.acwr = week.load / chronic
        return week

    acwr_before = week.load / chronic
    factor, iterations = 1.0, 0

    def scale_loop() -> None:
        nonlocal factor, iterations
        n = 0
        while over() and n < cfg.G2_MAX_ITERATIONS:
            f = cap * chronic / week.load
            _scale_week(week, f, cfg)
            refresh_week(week, cfg)
            factor *= f
            n += 1
            iterations += 1

    for _ in range(3):  # G3 fixes never raise load in practice; the loop is a guard
        scale_loop()
        while over() and week.hard_sessions:
            _convert_latest_hard(week, cfg)
            refresh_week(week, cfg)
            scale_loop()
        _g3_s4(week, cfg)
        _g3_long_run(week, cfg)
        enforce_p6(week, week.km, cfg)
        refresh_week(week, cfg)
        if not over():
            break
    if over():
        raise RuntimeError(f"Week {week.label}: governor could not bring ACWR to {cap}.")

    week.acwr = week.load / chronic
    week.governor = {"fired": True, "factor": factor, "iterations": iterations}
    week.add_trace("G2", "G3", "A-42", "A-48")
    week.add_note("G2", f"ACWR was {acwr_before:.3f} (> {cap}); the week was cut by factor {factor:.3f} "
                        f"to ACWR {week.acwr:.3f} (G2).")
    return week
