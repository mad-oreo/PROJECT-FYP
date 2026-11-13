"""L1-L3: long-run length."""
from __future__ import annotations

from typing import Any


def time_cap_km(easy_pace_s_per_km: float, cfg: Any) -> float:
    """Distance covered in 150 min at Z2 pace (L1 high branch, L2 marathon)."""
    return cfg.LONG_RUN_MAX_MIN * 60.0 / easy_pace_s_per_km


def l1_cap_km(week_km: float, easy_pace_s_per_km: float, cfg: Any) -> float:
    """L1: <= 30% of week km below 64 km; otherwise <= min(25% of week km, 150 min at Z2)."""
    if week_km < cfg.L1_THRESHOLD_KM:
        return cfg.L1_FRACTION_LOW * week_km
    return min(cfg.L1_FRACTION_HIGH * week_km, time_cap_km(easy_pace_s_per_km, cfg))


def l2_cap_km(distance: str, easy_pace_s_per_km: float, cfg: Any) -> float:
    """L2: 5K 12, 10K 16, HM 20 km (A-37); M = min(32 km, 150 min at Z2)."""
    cap = cfg.L2_CAP_KM[distance]
    if distance in cfg.L2_TIME_CAPPED_DISTANCES:
        cap = min(cap, time_cap_km(easy_pace_s_per_km, cfg))
    return cap


def long_run_km(week_km: float, distance: str, easy_pace_s_per_km: float, cfg: Any) -> tuple[float, str]:
    """OWN DESIGN (A-15): long run = the largest length allowed by L1 and L2.

    Returns (km, binding rule ID). L3: run at Z2 (A-10: no marathon-pace segments).
    """
    l1 = l1_cap_km(week_km, easy_pace_s_per_km, cfg)
    l2 = l2_cap_km(distance, easy_pace_s_per_km, cfg)
    return (l1, "L1") if l1 <= l2 else (l2, "L2")
