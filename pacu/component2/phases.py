"""P3 (Daniels Fig. 10.2 phases), A-1 PACU mapping, T1 taper weeks, P4 recovery weeks, P5 targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .models import NORMAL, RACE_WEEK, RECOVERY, TAPER


@dataclass(frozen=True)
class WeekPhase:
    plan_index: int
    daniels_phase: str
    pacu_phase: str
    week_type: str


def phase_lengths(n_weeks: int, cfg: Any) -> dict[str, int]:
    """P3: each phase's length = how many of its Fig. 10.2 week numbers are <= N."""
    return {p: sum(1 for w in cfg.DANIELS_PHASE_WEEKS[p] if w <= n_weeks) for p in cfg.DANIELS_PHASE_ORDER}


def daniels_phases(n_weeks: int, cfg: Any) -> list[str]:
    """P3: Daniels phase of plan weeks 1..N, phases in order I -> II -> III -> IV."""
    out: list[str] = []
    for p, length in phase_lengths(n_weeks, cfg).items():
        out.extend([p] * length)
    return out


def taper_length(distance: str, n_weeks: int, cfg: Any) -> int:
    """T1: 1 week (5K/10K), 2 (HM), 3 (M); at least 1 non-taper week must remain.

    OWN DESIGN (A-28): taper length = min(T1, N - 1).
    """
    return min(cfg.TAPER_WEEKS[distance], n_weeks - 1)


def plan_phases(n_weeks: int, distance: str, cfg: Any) -> list[WeekPhase]:
    """P3 + A-1 + T1 + P4: phase and week type of every plan week.

    OWN DESIGN (A-1): I = base, II = build, III = peak, IV = peak except its
    last T1 weeks = taper. OWN DESIGN (A-28): taper/race overrides any phase.
    P4: every 4th plan week is a recovery week unless it is a taper week.
    """
    taper = taper_length(distance, n_weeks, cfg)
    out = []
    for k, dp in enumerate(daniels_phases(n_weeks, cfg), start=1):
        if k > n_weeks - taper:
            pacu, wtype = "taper", (RACE_WEEK if k == n_weeks else TAPER)
        else:
            pacu = cfg.PACU_PHASE_OF_DANIELS[dp]
            wtype = RECOVERY if k % cfg.RECOVERY_WEEK_EVERY == 0 else NORMAL
        out.append(WeekPhase(k, dp, pacu, wtype))
    return out


def easy_share_target(daniels_phase: Optional[str], cfg: Any) -> float:
    """P5: easy-share target by Daniels phase. OWN DESIGN (A-41)."""
    return cfg.EASY_SHARE_TARGET[daniels_phase] if daniels_phase else 1.0
