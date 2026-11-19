"""V1-V4: weekly volume levels and the entry check (P4 recovery weeks applied here too)."""
from __future__ import annotations

from typing import Any, Optional, Sequence

from .capacity import v2_step_km
from .models import Message, RACE_WEEK, RECOVERY, TAPER
from .phases import WeekPhase


def below_entry_minimum(distance: str, current_km: float, cfg: Any) -> bool:
    """V4: current km below the distance's entry minimum. OWN DESIGN (A-35)."""
    return current_km < cfg.ENTRY_MIN_KM[distance]


def entry_suggestions(distance: str, current_km: float, cfg: Any) -> list[Message]:
    """V4 / A-11: shorter distances whose entry minimum is met, plus a later-race note."""
    out: list[Message] = []
    order = list(cfg.DISTANCES)
    for d in order[: order.index(distance)]:
        if not below_entry_minimum(d, current_km, cfg):
            out.append(Message(
                f"TRY_{d}",
                f"{d}: your {current_km:g} km/week meets its entry minimum of {cfg.ENTRY_MIN_KM[d]:g} km/week.",
            ))
    out.append(Message(
        "CHOOSE_LATER_RACE",
        f"Build up to at least {cfg.ENTRY_MIN_KM[distance]:g} km/week first, then choose a later {distance} race.",
    ))
    return out


def peak_target_km(distance: str, capacity: str, cfg: Any) -> float:
    """V3 peak target by distance and capacity."""
    return cfg.PEAK_TARGET_KM[distance][capacity]


def weekly_levels(
    phases: Sequence[WeekPhase], current_km: float, capacity: str, distance: str, cfg: Any
) -> tuple[list[Optional[float]], list[Message]]:
    """V1-V3 + P4 for non-taper weeks. Taper weeks are returned as None (filled by T2).

    V1: week 1 level = current km.
    V2: hold the level for 3 weeks, then a P4 recovery week, then level += step.
    V3: the level never exceeds the peak target. OWN DESIGN (A-6): at or above the
        target, hold the current level with no steps and add ABOVE_PEAK_TARGET.
    P4: recovery week = 80% of the previous week's planned level (A-40).
    """
    notes: list[Message] = []
    peak = peak_target_km(distance, capacity, cfg)
    above = current_km >= peak
    if above:
        notes.append(Message(
            "ABOVE_PEAK_TARGET",
            f"Current {current_km:g} km/week is at or above the {peak:g} km/week peak target; "
            f"the level is held with no steps (V3, A-6).",
        ))
    step = v2_step_km(capacity, cfg)
    cycle = cfg.V2_HOLD_WEEKS + 1
    level = float(current_km)
    levels: list[Optional[float]] = []
    for ph in phases:
        if ph.week_type in (TAPER, RACE_WEEK):
            levels.append(None)
            continue
        if ph.week_type == RECOVERY:
            levels.append(cfg.RECOVERY_WEEK_FRACTION * levels[-1])  # P4, A-40
            continue
        if ph.plan_index > 1 and (ph.plan_index - 1) % cycle == 0 and not above:
            level = min(level + step, peak)  # V2 step, V3 cap
        levels.append(level)
    return levels, notes
