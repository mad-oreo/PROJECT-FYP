"""PACU Component 2: staged crisp IF-THEN training plan engine.

Public API:
- generate_plan(inputs, cfg=config) -> PlanResult          (Section 5 pipeline)
- govern_week(week, previous_loads, config) -> Week         (G1-G3, Component 3 hook, G5)
- make_recovery_week(plan, week_label) -> PlanResult        (Component 3 hook, A-30)
- change_long_run_day(plan, new_weekday, from_week_label)   (Component 3 hook, A-26)
- clear_injury_flag(plan, from_week_label) -> PlanResult    (Component 3 hook, A-9)
"""
from .engine import change_long_run_day, clear_injury_flag, generate_plan, make_recovery_week
from .governor import govern_week
from .models import PlanInputs, PlanResult, Session, Week

__all__ = [
    "PlanInputs", "PlanResult", "Session", "Week",
    "generate_plan", "govern_week", "make_recovery_week", "change_long_run_day", "clear_injury_flag",
]
