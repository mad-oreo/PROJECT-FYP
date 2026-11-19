"""C rules: recovery score, bands and capacity."""
from __future__ import annotations

from typing import Any, Sequence

LOW, MODERATE, HIGH = "Low", "Moderate", "High"


def recovery_score(answers: Sequence[int]) -> int:
    """Recovery score = q1 + q2 + q3 (sleep, muscle recovery, freshness), range 3-15."""
    return int(sum(answers))


def recovery_band(score: int, cfg: Any) -> str:
    """OWN DESIGN (A-34): Low 3-7, Moderate 8-11, High 12-15."""
    if score <= cfg.RECOVERY_LOW_MAX:
        return LOW
    if score >= cfg.RECOVERY_HIGH_MIN:
        return HIGH
    return MODERATE


def mileage_band(km: float, cfg: Any) -> str:
    """OWN DESIGN (A-34): Low < 20, Moderate 20-40 inclusive, High > 40 km/week."""
    if km < cfg.MILEAGE_LOW_BELOW_KM:
        return LOW
    if km > cfg.MILEAGE_HIGH_ABOVE_KM:
        return HIGH
    return MODERATE


def fired_rules(km: float, score: int, cfg: Any) -> list[tuple[str, str]]:
    """Every C rule whose IF part holds, as (rule ID, capacity), in priority order.

    OWN DESIGN (A-34): C1 Recovery Low -> Conservative; C2 Mileage Low -> Conservative;
    C3 Mileage High AND Recovery High -> Progressive; C4 otherwise -> Standard.
    """
    rec, mil = recovery_band(score, cfg), mileage_band(km, cfg)
    candidates = {
        "C1": (rec == LOW, "Conservative"),
        "C2": (mil == LOW, "Conservative"),
        "C3": (mil == HIGH and rec == HIGH, "Progressive"),
    }
    fired = [(rid, cap) for rid, (cond, cap) in candidates.items() if cond]
    if not fired:
        fired = [("C4", "Standard")]
    order = {rid: i for i, rid in enumerate(cfg.C_RULE_PRIORITY)}
    return sorted(fired, key=lambda rc: order[rc[0]])


def decide_capacity(km: float, answers: Sequence[int], cfg: Any) -> tuple[str, str, int]:
    """C rules: return (capacity, winning rule ID, recovery score). Lowest priority number wins."""
    score = recovery_score(answers)
    rule_id, cap = fired_rules(km, score, cfg)[0]
    return cap, rule_id, score


def runs_per_week(capacity: str, cfg: Any) -> int:
    return cfg.RUNS_PER_WEEK[capacity]


def hard_sessions(capacity: str, cfg: Any) -> int:
    return cfg.HARD_SESSIONS_PER_WEEK[capacity]


def v2_step_km(capacity: str, cfg: Any) -> float:
    """V2 step = 1.6 km x runs per week (4.8 / 6.4 / 8.0)."""
    return cfg.V2_KM_PER_RUN * cfg.RUNS_PER_WEEK[capacity]
