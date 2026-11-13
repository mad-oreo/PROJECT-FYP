"""Data model for PACU Component 2 (Section 3 inputs, Section 6 outputs).

Internal units: km (float), pace in seconds per km, durations in minutes,
dates as ``datetime.date``. Rounding happens only in serialize.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

# Slot names (S1)
LONG, HARD, EASY, RACE = "LONG", "HARD", "EASY", "RACE"
# Week types (P4, T1, A-18)
HOLD, NORMAL, RECOVERY, TAPER, RACE_WEEK = "hold", "normal", "recovery", "taper", "race"


@dataclass
class Message:
    """A coded warning, note or advisory."""

    code: str
    message: str


@dataclass
class PlanInputs:
    """User inputs (Section 3). Component 1's predicted times arrive as plain numbers."""

    target_distance: str
    predicted_times_s: dict[str, float]
    easy_pace_s_per_km: float
    current_weekly_km: float
    recovery_answers: tuple[int, int, int]
    injury_flag: bool
    race_date: date
    start_date: date = field(default_factory=date.today)
    long_run_weekday: Optional[int] = None
    max_hr: Optional[int] = None
    override_entry_minimum: bool = False


@dataclass
class Paces:
    """Zone pace targets in s/km (Z rules, A-12, A-33)."""

    easy: float  # Z2
    z1: float
    z3_tempo: float  # short-track tempo (A-12)
    z3_race: float  # long-track race-pace run (A-12)
    z4: float
    z5: float
    race: float  # predicted pace of the target distance
    predicted: dict[str, float]  # predicted pace per distance

    def for_zone(self, zone: str) -> float:
        """Default pace for a zone (Z rules)."""
        return {"Z1": self.z1, "Z2": self.easy, "Z3": self.z3_tempo, "Z4": self.z4, "Z5": self.z5}[zone]


@dataclass
class Segment:
    """One block of a session (S5, S6)."""

    kind: str  # warmup | rep | jog | steady | cooldown
    km: float
    zone: Optional[str]
    pace_s_per_km: float

    @property
    def minutes(self) -> float:
        """S6: segment minutes = km x pace."""
        return self.km * self.pace_s_per_km / 60.0


@dataclass
class MainSet:
    """The hard part of a HARD session, kept so S7 sizing can be redone under G2 (A-48)."""

    workout: str  # workout code, e.g. "Z4_1K_REPS"
    label: str  # human-readable name used in the title
    zone: str
    pace_s_per_km: float
    unit: str  # "m" distance reps, "s" time reps, "cont" continuous
    nominal_len: float  # rep length before any S7 halving (m or s); 0 for continuous
    jog_s: float
    budget_km: float  # P5 hard budget for this session (A-19)
    week_km_ref: float  # week km the S4 cap was computed on
    rule_ids: tuple[str, ...] = ()  # content-table rule IDs for the trace
    target_km: Optional[float] = None  # A-21 race-week target / A-24 fixed 20 min run
    scale: float = 1.0  # cumulative G2 factor (A-48)
    cap_override_km: Optional[float] = None  # G3 S4 re-check against actual week km (A-48)
    # results of sizing (S7 / A-25)
    reps: int = 0
    rep_len: float = 0.0
    allowance_km: float = 0.0
    s4_class: str = ""
    halvings: int = 0

    @property
    def rep_km(self) -> float:
        """Length of one rep in km (time reps converted at the zone pace, S7)."""
        if self.unit == "m":
            return self.rep_len / 1000.0
        if self.unit == "s":
            return self.rep_len / self.pace_s_per_km
        return self.allowance_km  # continuous: one block

    @property
    def main_km(self) -> float:
        """Total km at the main zone."""
        if self.unit == "cont":
            return self.allowance_km if self.reps else 0.0
        return self.reps * self.rep_km


@dataclass
class Session:
    """One run on one date (Section 6)."""

    date: date
    slot: str  # LONG | HARD | EASY | RACE
    title: str = ""
    main_zone: Optional[str] = None
    segments: list[Segment] = field(default_factory=list)
    main_set: Optional[MainSet] = None
    warmup_min: float = 0.0  # S5 warm-up and cool-down minutes (each)
    strides: int = 0
    run_walk_ok: bool = False
    rule_trace: list[str] = field(default_factory=list)
    notes: list[Message] = field(default_factory=list)
    load: Optional[float] = None
    target_rpe: Optional[float] = None
    hr_range: Optional[tuple[Optional[int], Optional[int]]] = None

    @property
    def weekday(self) -> int:
        return self.date.weekday()

    @property
    def km(self) -> float:
        return sum(s.km for s in self.segments)

    @property
    def minutes(self) -> float:
        """S6: session duration = sum of segment minutes."""
        return sum(s.minutes for s in self.segments)

    @property
    def easy_km(self) -> float:
        return sum(s.km for s in self.segments if s.zone in ("Z1", "Z2"))

    @property
    def reps(self) -> Optional[int]:
        if self.main_set is None or self.main_set.unit == "cont":
            return None
        return self.main_set.reps

    @property
    def rep_length(self) -> Optional[str]:
        if self.main_set is None or self.main_set.unit == "cont":
            return None
        if self.main_set.unit == "m":
            return f"{self.main_set.rep_len:.0f} m"
        return _fmt_seconds(self.main_set.rep_len)

    def add_trace(self, *rule_ids: str) -> None:
        for rid in rule_ids:
            if rid not in self.rule_trace:
                self.rule_trace.append(rid)

    def add_note(self, code: str, message: str) -> None:
        if not any(n.code == code for n in self.notes):
            self.notes.append(Message(code, message))

    def has_note(self, code: str) -> bool:
        return any(n.code == code for n in self.notes)


@dataclass
class WeekSpec:
    """Planned facts about a week, fixed before sessions are built (P, V, T rules)."""

    label: str
    plan_index: Optional[int]  # 1..N; None for hold weeks
    start_date: date
    end_date: date
    daniels_phase: Optional[str]  # I-IV; None for hold weeks
    pacu_phase: str  # hold | base | build | peak | taper
    week_type: str  # hold | normal | recovery | taper | race
    level_km: float
    long_run_weekday: int
    hard_paused: bool = False  # A-9 injury flag
    s2_transition: bool = False  # A-26 first re-laid week after a long-run day change


@dataclass
class Week:
    """A built and governed week (Section 6)."""

    spec: WeekSpec
    sessions: list[Session] = field(default_factory=list)
    km: float = 0.0
    easy_km: float = 0.0
    easy_share: float = 0.0
    load: float = 0.0
    chronic_load: float = 0.0
    acwr: float = 0.0
    governor: dict[str, Any] = field(default_factory=lambda: {"fired": False, "factor": 1.0, "iterations": 0})
    rule_trace: list[str] = field(default_factory=list)
    notes: list[Message] = field(default_factory=list)
    ctx: Any = field(default=None, repr=False, compare=False)  # PlanContext

    # convenience accessors for the spec
    @property
    def label(self) -> str:
        return self.spec.label

    @property
    def start_date(self) -> date:
        return self.spec.start_date

    @property
    def end_date(self) -> date:
        return self.spec.end_date

    @property
    def daniels_phase(self) -> Optional[str]:
        return self.spec.daniels_phase

    @property
    def pacu_phase(self) -> str:
        return self.spec.pacu_phase

    @property
    def week_type(self) -> str:
        return self.spec.week_type

    @property
    def level_km(self) -> float:
        return self.spec.level_km

    @property
    def runs(self) -> list[Session]:
        """All sessions except the race (A-4)."""
        return [s for s in self.sessions if s.slot != RACE]

    @property
    def hard_sessions(self) -> list[Session]:
        return [s for s in self.sessions if s.slot == HARD]

    def add_trace(self, *rule_ids: str) -> None:
        for rid in rule_ids:
            if rid not in self.rule_trace:
                self.rule_trace.append(rid)

    def add_note(self, code: str, message: str) -> None:
        if not any(n.code == code for n in self.notes):
            self.notes.append(Message(code, message))

    def has_note(self, code: str) -> bool:
        return any(n.code == code for n in self.notes)


@dataclass
class PlanContext:
    """Everything fixed for the whole plan, shared by every week."""

    inputs: PlanInputs
    cfg: Any
    distance: str
    track: str
    capacity: str
    paces: Paces
    n_weeks: int
    taper_len: int
    phase_lengths: dict[str, int]
    peak_target_km: float


@dataclass
class PlanResult:
    """The full plan (Section 6)."""

    status: str  # "OK" | "BELOW_ENTRY_MINIMUM"
    inputs: PlanInputs
    recovery_score: int
    capacity: str
    c_rule: str
    track: str
    warnings: list[Message] = field(default_factory=list)
    notes: list[Message] = field(default_factory=list)
    advisories: list[Message] = field(default_factory=list)
    suggestions: list[Message] = field(default_factory=list)
    N: int = 0
    hold_weeks: int = 0
    phase_lengths: dict[str, int] = field(default_factory=dict)
    weeks: list[Week] = field(default_factory=list)
    race: Optional[dict[str, Any]] = None
    summary: dict[str, Any] = field(default_factory=dict)
    context: Optional[PlanContext] = field(default=None, repr=False, compare=False)

    def week(self, label: str) -> Week:
        for w in self.weeks:
            if w.label == label:
                return w
        raise KeyError(f"No week labelled {label!r}")

    def week_index(self, label: str) -> int:
        for i, w in enumerate(self.weeks):
            if w.label == label:
                return i
        raise KeyError(f"No week labelled {label!r}")


def _fmt_seconds(seconds: float) -> str:
    """Format a rep duration: 90 -> '90 s', 180 -> '3 min', 150 -> '2:30 min'."""
    s = int(round(seconds))
    if s < 120 and s % 60:
        return f"{s} s"
    m, rem = divmod(s, 60)
    return f"{m} min" if rem == 0 else f"{m}:{rem:02d} min"
