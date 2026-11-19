"""Z rules: zone paces, load RPE and heart-rate ranges."""
from __future__ import annotations

from typing import Any, Optional

from .models import Paces, PlanInputs


def predicted_paces(predicted_times_s: dict[str, float], cfg: Any) -> dict[str, float]:
    """Z rules: predicted pace = predicted time / distance (s/km)."""
    return {d: predicted_times_s[d] / cfg.DISTANCE_KM[d] for d in cfg.DISTANCES}


def build_paces(inputs: PlanInputs, cfg: Any) -> Paces:
    """Z1-Z5 pace targets (A-33), with the Z3 paces from A-12."""
    pred = predicted_paces(inputs.predicted_times_s, cfg)
    easy = float(inputs.easy_pace_s_per_km)
    # OWN DESIGN (A-12): short-track tempo = midpoint of predicted marathon and HM pace.
    z3_tempo = (pred["M"] + pred["HM"]) / 2.0
    # OWN DESIGN (A-12): long-track race-pace run = marathon pace for M, HM pace for HM.
    z3_race = pred[inputs.target_distance] if inputs.target_distance in ("HM", "M") else z3_tempo
    return Paces(
        easy=easy,
        z1=easy + cfg.Z1_PACE_OFFSET_S_PER_KM,  # OWN DESIGN (A-33)
        z3_tempo=z3_tempo,
        z3_race=z3_race,
        z4=pred[cfg.Z4_PACE_DISTANCE],  # OWN DESIGN (A-33)
        z5=pred[cfg.Z5_PACE_DISTANCE],  # OWN DESIGN (A-33)
        race=pred[inputs.target_distance],
        predicted=pred,
    )


def fmt_pace(s_per_km: float) -> str:
    """Format a pace as 'm:ss/km' (output only)."""
    total = int(round(s_per_km))
    return f"{total // 60}:{total % 60:02d}/km"


def fmt_time(seconds: float) -> str:
    """Format a duration as 'h:mm:ss' or 'm:ss' (output only)."""
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def load_rpe(zone: str, cfg: Any) -> float:
    """RPE used for load (S6): CR10 range midpoint (A-33)."""
    return cfg.ZONE_LOAD_RPE[zone]


def is_easy(zone: Optional[str], cfg: Any) -> bool:
    """Z rules: 'easy' = Z1 + Z2."""
    return zone in cfg.EASY_ZONES


def hr_range(zone: Optional[str], max_hr: Optional[int], cfg: Any) -> Optional[tuple[Optional[int], Optional[int]]]:
    """Z rules: % max HR band in bpm, only when max HR is given."""
    if max_hr is None or zone is None:
        return None
    lo, hi = cfg.ZONE_HR_PCT[zone]
    return (
        None if lo is None else round(lo / 100.0 * max_hr),
        None if hi is None else round(hi / 100.0 * max_hr),
    )
