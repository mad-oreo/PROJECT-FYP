"""T2: taper volume levels."""
from __future__ import annotations

from typing import Any, Optional, Sequence

from .models import NORMAL, RACE_WEEK, TAPER
from .phases import WeekPhase


def taper_reference_index(phases: Sequence[WeekPhase]) -> int:
    """OWN DESIGN (A-8): the taper reference is the last non-recovery, non-taper week."""
    idx = [i for i, ph in enumerate(phases) if ph.week_type == NORMAL]
    if not idx:
        raise ValueError("No non-recovery week before the taper (A-8).")
    return idx[-1]


def taper_levels(levels: Sequence[Optional[float]], phases: Sequence[WeekPhase], cfg: Any) -> list[float]:
    """T2: each non-race taper week = 75% of the week before (A-39); race week = 50%.

    For the first taper week, 'the week before' is the A-8 reference level.
    """
    out = list(levels)
    prev = out[taper_reference_index(phases)]
    for i, ph in enumerate(phases):
        if ph.week_type == TAPER:
            out[i] = cfg.TAPER_WEEK_FRACTION * prev
        elif ph.week_type == RACE_WEEK:
            out[i] = cfg.RACE_WEEK_FRACTION * prev
        else:
            continue
        prev = out[i]
    assert all(v is not None for v in out)
    return [float(v) for v in out]  # type: ignore[arg-type]
