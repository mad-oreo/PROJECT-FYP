"""S6: planned training load (session-RPE) and week totals."""
from __future__ import annotations

from typing import Any, Optional

from .models import RACE, Session, Week


def session_load(session: Session, cfg: Any) -> Optional[float]:
    """S6: planned load of one session; None for the race (A-4).

    "session" (default): session duration x RPE of the session's main zone
    (Foster et al., 2001). "segment" (A-17): sum of segment minutes x segment-zone RPE.
    """
    if session.slot == RACE:
        return None
    if cfg.LOAD_METHOD == "session":
        return session.minutes * cfg.ZONE_LOAD_RPE[session.main_zone]
    if cfg.LOAD_METHOD == "segment":
        return sum(seg.minutes * cfg.ZONE_LOAD_RPE[seg.zone] for seg in session.segments)
    raise ValueError(f"Unknown LOAD_METHOD {cfg.LOAD_METHOD!r}")


def refresh_totals(week: Week, cfg: Any) -> None:
    """Recompute session loads and week km, easy km, easy share and load (race excluded, A-4)."""
    for s in week.sessions:
        s.load = session_load(s, cfg)
        s.target_rpe = None if s.slot == RACE else cfg.ZONE_LOAD_RPE[s.main_zone]
    runs = week.runs
    week.km = sum(s.km for s in runs)
    week.easy_km = sum(seg.km for s in runs for seg in s.segments if seg.zone in cfg.EASY_ZONES)
    week.easy_share = week.easy_km / week.km if week.km > 0 else 1.0
    week.load = sum(s.load for s in runs if s.load is not None)


def baseline_load(current_km: float, easy_pace_s_per_km: float, cfg: Any) -> float:
    """G6 cold start: current km x easy pace (min/km) x Z2 RPE (3.5). OWN DESIGN (A-42)."""
    return current_km * (easy_pace_s_per_km / 60.0) * cfg.ZONE_LOAD_RPE[cfg.BASELINE_ZONE]
