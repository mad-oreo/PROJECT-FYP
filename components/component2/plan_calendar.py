"""P1, P2, P2b: plan length, hold weeks and week dates.

Named plan_calendar (not calendar) so it cannot shadow Python's calendar module.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from .models import Message


@dataclass
class CalendarInfo:
    """Result of P1."""

    n_weeks: int
    hold_weeks: int
    leftover_days: int
    week_dates: list[tuple[date, date]]  # plan weeks 1..N (start, end)
    hold_dates: list[tuple[date, date]]  # hold weeks H1..Hh (start, end)


def plan_calendar(start_date: date, race_date: date, cfg: Any) -> CalendarInfo:
    """P1: N = whole 7-day weeks from start to race (inclusive), capped at 24.

    OWN DESIGN (A-7): weeks are anchored so week N ends on race day; leftover
    0-6 days before the first week are unscheduled.
    OWN DESIGN (A-18): whole weeks beyond 24 become hold weeks before week 1.
    OWN DESIGN (A-28): fewer than 2 whole weeks is an error.
    """
    days = (race_date - start_date).days + 1
    total = days // cfg.DAYS_PER_WEEK
    if total < cfg.MIN_PLAN_WEEKS:
        raise ValueError(
            f"Race is too close: {total} whole week(s) available, at least "
            f"{cfg.MIN_PLAN_WEEKS} needed (A-28)."
        )
    n = min(total, cfg.MAX_PLAN_WEEKS)
    hold = total - n
    week = timedelta(days=cfg.DAYS_PER_WEEK)
    week_dates = []
    for k in range(1, n + 1):
        end = race_date - week * (n - k)
        week_dates.append((end - timedelta(days=cfg.DAYS_PER_WEEK - 1), end))
    first_start = week_dates[0][0]
    hold_dates = []
    for j in range(1, hold + 1):
        end = first_start - timedelta(days=1) - week * (hold - j)
        hold_dates.append((end - timedelta(days=cfg.DAYS_PER_WEEK - 1), end))
    return CalendarInfo(n, hold, days % cfg.DAYS_PER_WEEK, week_dates, hold_dates)


def minimum_weeks(distance: str, capacity: str, cfg: Any) -> int:
    """P2: 6 for 5K/10K, 9 for HM, 12 for M, 18 for M with Conservative capacity."""
    if distance == "M" and capacity == "Conservative":
        return cfg.MIN_WEEKS_CONSERVATIVE_M
    return cfg.MIN_WEEKS[distance]


def length_messages(distance: str, capacity: str, n_weeks: int, cfg: Any) -> tuple[list[Message], list[Message]]:
    """P2 warning and P2b note. Returns (warnings, notes)."""
    warnings: list[Message] = []
    notes: list[Message] = []
    minimum = minimum_weeks(distance, capacity, cfg)
    if n_weeks < minimum:
        warnings.append(Message(
            "PLAN_SHORTER_THAN_MINIMUM",
            f"The plan has {n_weeks} weeks; at least {minimum} are recommended for this distance "
            f"and capacity (P2). The plan is still generated.",
        ))
    if distance == "5K" and not (cfg.FIVE_K_RECOMMENDED_MIN_WEEKS <= n_weeks <= cfg.FIVE_K_RECOMMENDED_MAX_WEEKS):
        notes.append(Message(
            "5K_RECOMMENDED_8_TO_12_WEEKS",
            f"5K plans work best at {cfg.FIVE_K_RECOMMENDED_MIN_WEEKS}-{cfg.FIVE_K_RECOMMENDED_MAX_WEEKS} "
            f"weeks (about 9); this plan has {n_weeks} (P2b).",
        ))
    return warnings, notes
