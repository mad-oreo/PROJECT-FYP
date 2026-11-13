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
