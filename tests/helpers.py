"""Shared test helpers (not a test module)."""
from __future__ import annotations

from datetime import date

from pacu.component2 import config
from pacu.component2.models import PlanInputs

RIEGEL_EXPONENT = 1.06


def riegel_times(t5k_s: float) -> dict[str, float]:
    """Fill all four predicted times from a 5K time: T2 = T1 x (D2/D1)^1.06."""
    return {d: t5k_s * (config.DISTANCE_KM[d] / 5.0) ** RIEGEL_EXPONENT for d in config.DISTANCES}


def make_inputs(**kw) -> PlanInputs:
    """A valid PlanInputs with sensible defaults, overridable per test."""
    base = dict(
        target_distance="10K",
        predicted_times_s=riegel_times(27.5 * 60),
        easy_pace_s_per_km=400.0,
        current_weekly_km=30.0,
        recovery_answers=(4, 3, 3),
        injury_flag=False,
        race_date=date(2027, 3, 28),
        start_date=date(2026, 12, 7),
        long_run_weekday=None,
        max_hr=None,
        override_entry_minimum=False,
    )
    base.update(kw)
    return PlanInputs(**base)


def make_ctx(inputs: PlanInputs, capacity: str | None = None, cfg=config):
    """A PlanContext built straight from the rule modules (no engine)."""
    from pacu.component2.capacity import decide_capacity
    from pacu.component2.models import PlanContext
    from pacu.component2.phases import phase_lengths, taper_length
    from pacu.component2.plan_calendar import plan_calendar
    from pacu.component2.volume import peak_target_km
    from pacu.component2.zones import build_paces

    cap = capacity or decide_capacity(inputs.current_weekly_km, inputs.recovery_answers, cfg)[0]
    cal = plan_calendar(inputs.start_date, inputs.race_date, cfg)
    d = inputs.target_distance
    return PlanContext(
        inputs=inputs, cfg=cfg, distance=d, track=cfg.TRACK_OF[d], capacity=cap,
        paces=build_paces(inputs, cfg), n_weeks=cal.n_weeks,
        taper_len=taper_length(d, cal.n_weeks, cfg), phase_lengths=phase_lengths(cal.n_weeks, cfg),
        peak_target_km=peak_target_km(d, cap, cfg),
    )
