"""PACU Component 2 configuration: every number the rule engine uses.

Each constant names its rule ID and its source:
- ``SOURCE: <citation> [log n]``: literature-based. "log n" is the row in the
  rule-specification verification log (checked 11-13 Nov 2026). Daniels page
  numbers are not verified yet, so Daniels tags say "page TBC".
- ``OWN DESIGN (A-n)``: Naji's own design; see ASSUMPTIONS.md for A-n.
- ``SOURCE: TBC``: not covered by the source map (``LAYOUT`` and
  ``KNOPP_WEEKLY_INCREASE_PCT``).
- ``DEFINITION``: a unit, a standard definition or a numerical tolerance, not a
  training rule, so it needs no source (``DISTANCE_KM``, ``DAYS_PER_WEEK``,
  ``ACWR_TOLERANCE``, ``FLOAT_EPS``).

No other module may hard-code a threshold. To run with different values (for
persona testing) use :func:`with_overrides`, e.g. ``with_overrides(LOAD_METHOD="segment")``.
"""
from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

# ---------------------------------------------------------------------------
# Distances and tracks
# ---------------------------------------------------------------------------
DISTANCES = ("5K", "10K", "HM", "M")
# Standard race distances in km. DEFINITION
DISTANCE_KM = {"5K": 5.0, "10K": 10.0, "HM": 21.0975, "M": 42.195}
TRACK_OF = {"5K": "short", "10K": "short", "HM": "long", "M": "long"}
CAPACITIES = ("Conservative", "Standard", "Progressive")

# ---------------------------------------------------------------------------
# Z rules: five-zone intensity model
# ---------------------------------------------------------------------------
ZONES = ("Z1", "Z2", "Z3", "Z4", "Z5")
# Zone names, % max HR bands and RPE (CR10) ranges.
# SOURCE: Knopp et al. (2024), Table 2, p. 5 [log 5] (Knopp adapted the model
# from Jamnick et al. and Seiler; do not credit Knopp as originator).
# Zone <-> Daniels E/M/T heart-rate bands: SOURCE: Daniels (2022), Ch. 4, page TBC [log 23].
ZONE_NAMES = {
    "Z1": "Slow endurance",
    "Z2": "Extensive endurance",
    "Z3": "Intensive endurance",
    "Z4": "Threshold",
    "Z5": "High intensity",
}
ZONE_HR_PCT = {  # (low %, high %) of max HR; None = open-ended
    "Z1": (None, 72),
    "Z2": (73, 80),
    "Z3": (81, 86),
    "Z4": (87, 92),
    "Z5": (93, None),
}
ZONE_RPE_RANGE = {"Z1": (1, 2), "Z2": (3, 4), "Z3": (5, 6), "Z4": (7, 8), "Z5": (9, 10)}
# RPE used for load = midpoint of each CR10 range. OWN DESIGN (A-33)
ZONE_LOAD_RPE = {"Z1": 1.5, "Z2": 3.5, "Z3": 5.5, "Z4": 7.5, "Z5": 9.5}
# Pace targets: Z1 = easy + 30 s/km, Z2 = easy, Z4 = predicted 10K pace,
# Z5 = predicted 5K pace. OWN DESIGN (A-33). Z3 pace: OWN DESIGN (A-12), see zones.py.
Z1_PACE_OFFSET_S_PER_KM = 30.0
Z4_PACE_DISTANCE = "10K"
Z5_PACE_DISTANCE = "5K"
# "Easy" in every share calculation = Z1 + Z2 (RPE 1-4). SOURCE: Campos et al. (2022),
# p. 306 (low intensity = RPE 1-4) [log 15].
EASY_ZONES = ("Z1", "Z2")

# ---------------------------------------------------------------------------
# C rules: recovery score and capacity
# ---------------------------------------------------------------------------
# Three recovery questions (sleep, muscle recovery, freshness), each 1-5, summed.
# SOURCE: Daniels (2022), Ch. 2, Table 2.1 "Stress Table", page TBC [log 35];
# Goldberg et al. (2025), Abstract [log 37]; Smyth et al. (2022), s. 2.1.3, p. 793 [log 36].
RECOVERY_Q_COUNT = 3
RECOVERY_Q_MIN = 1
RECOVERY_Q_MAX = 5
# Recovery bands (sum 3-15): Low 3-7, Moderate 8-11, High 12-15. OWN DESIGN (A-34)
RECOVERY_LOW_MAX = 7
RECOVERY_HIGH_MIN = 12
# Mileage bands: Low < 20, Moderate 20-40 inclusive, High > 40 km/week. OWN DESIGN (A-34)
MILEAGE_LOW_BELOW_KM = 20.0
MILEAGE_HIGH_ABOVE_KM = 40.0
# Rules C1-C4 and their priority order (lowest number wins). OWN DESIGN (A-34)
C_RULE_PRIORITY = ("C1", "C2", "C3", "C4")
# Runs per week. SOURCE: Daniels (2022), Ch. 16 "Novice Training", page TBC [log 24];
# Knopp et al. (2024), Table 3 (4.1 +/- 0.9 sessions) [log 9].
RUNS_PER_WEEK = {"Conservative": 3, "Standard": 4, "Progressive": 5}
# Hard sessions per week in build/peak. SOURCE: Daniels (2022), Ch. 16, page TBC [log 24];
# Knopp et al. (2024), Discussion p. 10 [log 12], citing Midgley et al. (2007) and
# Boullosa et al. (2020) (secondary: as cited in Knopp et al., 2024).
HARD_SESSIONS_PER_WEEK = {"Conservative": 1, "Standard": 2, "Progressive": 2}
# V2 step = 1.6 km per weekly run. SOURCE: Daniels (2022), Ch. 4 "Training Suggestions";
# Ch. 13 "Phase I", page TBC [log 21].
V2_KM_PER_RUN = 1.6

# ---------------------------------------------------------------------------
# P rules: plan length and phases
# ---------------------------------------------------------------------------
DAYS_PER_WEEK = 7  # DEFINITION
# P1: 24-week cap. SOURCE: Daniels (2022), Ch. 10 "Adapt the Phase Lengths as Necessary", page TBC [log 17].
MAX_PLAN_WEEKS = 24
# A-28: a plan needs at least 2 whole weeks (1 non-taper week + race week). OWN DESIGN (A-28)
MIN_PLAN_WEEKS = 2
# P2: minimum plan length by distance.
# 5K/10K 6 and HM 9: OWN DESIGN (A-47), built on Daniels (2022), Ch. 10, Fig. 10.2 [log 17].
# Marathon 12: SOURCE: Feely et al. (2023), Abstract; Smyth et al. (2022), p. 794;
# Knopp et al. (2024), p. 6 [log 34].
# Conservative marathon 18: SOURCE: Daniels (2022), Ch. 16, Table 16.2, page TBC [log 31].
MIN_WEEKS = {"5K": 6, "10K": 6, "HM": 9, "M": 12}
MIN_WEEKS_CONSERVATIVE_M = 18
# P2b: 5K recommended 8-12 weeks (about 9). SOURCE: Plateau et al. (2022), pp. 1-2;
# Relph et al. (2023), Methods [log 32, 33].
FIVE_K_RECOMMENDED_MIN_WEEKS = 8
FIVE_K_RECOMMENDED_MAX_WEEKS = 12
# P3: Daniels week numbers per phase. SOURCE: Daniels (2022), Ch. 10, Fig. 10.2, page TBC [log 17].
DANIELS_PHASE_WEEKS = {
    "I": (1, 2, 3, 13, 21, 23),
    "II": (7, 8, 9, 18, 19, 20),
    "III": (10, 11, 12, 14, 15, 16),
    "IV": (4, 5, 6, 17, 22, 24),
}
DANIELS_PHASE_ORDER = ("I", "II", "III", "IV")
# A-1 PACU phase mapping (Phase IV's last T1 weeks become taper). OWN DESIGN (A-1)
PACU_PHASE_OF_DANIELS = {"I": "base", "II": "build", "III": "peak", "IV": "peak"}
# P4: every 4th plan week is a recovery week with no hard sessions.
# SOURCE: Daniels (2022), Ch. 16 (4-week cycle plans), page TBC [log 26]; Feely et al. (2023), Introduction [log 16].
RECOVERY_WEEK_EVERY = 4
# P4: recovery week volume = 80% of the previous week's planned level. OWN DESIGN (A-40)
RECOVERY_WEEK_FRACTION = 0.80
# P5: easy-share target by Daniels phase (Phase I is "at least 90%"). OWN DESIGN (A-41)
EASY_SHARE_TARGET = {"I": 0.90, "II": 0.80, "III": 0.75, "IV": 0.80}
# P6: every week, easy km >= 70% of week km. SOURCE: Campos et al. (2022), Abstract p. 305;
# low intensity = RPE 1-4, p. 306 [log 14, 15].
MIN_EASY_SHARE = 0.70
# P7: plan-wide easy share about 80% (report only). SOURCE: Knopp et al. (2024), Key points p. 1 (78.8%) [log 6].
PLAN_EASY_SHARE_BENCHMARK = 0.80

# ---------------------------------------------------------------------------
# V rules: volume
# ---------------------------------------------------------------------------
# V2: hold the level for 3 weeks, then a recovery week, then step.
# SOURCE: Daniels (2022), Ch. 4 "Training Suggestions"; Ch. 13 "Phase I", page TBC [log 21].
V2_HOLD_WEEKS = 3
# V4 entry minimums (km/week). OWN DESIGN (A-35)
ENTRY_MIN_KM = {"5K": 5.0, "10K": 10.0, "HM": 15.0, "M": 25.0}
# V3 peak targets (km/week).
# Marathon Standard 58 and Progressive 75: SOURCE: Knopp et al. (2024), Results pp. 7-8
# (58.6 +/- 6.4 and 75.5 +/- 8.5 km) [log 8]. All other cells: OWN DESIGN (A-36).
PEAK_TARGET_KM = {
    "5K": {"Conservative": 25.0, "Standard": 30.0, "Progressive": 40.0},
    "10K": {"Conservative": 30.0, "Standard": 40.0, "Progressive": 50.0},
    "HM": {"Conservative": 35.0, "Standard": 45.0, "Progressive": 55.0},
    "M": {"Conservative": 45.0, "Standard": 58.0, "Progressive": 75.0},
}

# ---------------------------------------------------------------------------
# L rules: long run
# ---------------------------------------------------------------------------
# L1: <= 30% of week km below 64 km; otherwise <= min(25%, 150 min at Z2).
# SOURCE: Daniels (2022), Ch. 4 "Long Runs and Increasing Mileage", page TBC [log 19].
L1_THRESHOLD_KM = 64.0
L1_FRACTION_LOW = 0.30
L1_FRACTION_HIGH = 0.25
# 150 min long-run time cap. SOURCE: Daniels (2022), Ch. 4 "Training Suggestions", page TBC [log 20].
LONG_RUN_MAX_MIN = 150.0
# L2 caps by distance (km).
# Marathon 32 km: SOURCE: Knopp et al. (2024), Results p. 8; Conclusions point 4 [log 10].
# 5K 12, 10K 16, HM 20: OWN DESIGN (A-37).
L2_CAP_KM = {"5K": 12.0, "10K": 16.0, "HM": 20.0, "M": 32.0}
# L2 for the marathon is also capped by 150 min at Z2 (see LONG_RUN_MAX_MIN).
L2_TIME_CAPPED_DISTANCES = ("M",)
# L3: long run at Z2. SOURCE: Knopp et al. (2024), Table 2; Daniels (2022), Ch. 4 [log 5].
LONG_RUN_ZONE = "Z2"

# ---------------------------------------------------------------------------
# T rules: taper
# ---------------------------------------------------------------------------
# T1 taper length (weeks).
# Marathon 3: SOURCE: Knopp et al. (2024), Conclusions point 5; Feely et al. (2023), Introduction [log 16].
# HM 2: SOURCE: Bosquet et al. (2007), as cited in Knopp et al. (2024), Discussion p. 11 [log 13] (secondary).
# 5K/10K 1: OWN DESIGN (A-38).
TAPER_WEEKS = {"5K": 1, "10K": 1, "HM": 2, "M": 3}
# T2: non-race taper week = 75% of the week before.
# OWN DESIGN (A-39), inside Knopp et al. (2024), Results p. 9 (22-31% per week) [log 11].
TAPER_WEEK_FRACTION = 0.75
# T2: race week = 50% of the week before. SOURCE: Knopp et al. (2024), Results p. 9 (final week 46-54%) [log 11].
RACE_WEEK_FRACTION = 0.50
# T3: taper keeps intensity and frequency; race week has exactly 1 hard session.
# SOURCE: Bosquet et al. (2007), as cited in Knopp et al. (2024), Discussion p. 11 [log 13] (secondary). A-3.
RACE_WEEK_HARD_SESSIONS = 1

# ---------------------------------------------------------------------------
# S rules: sessions
# ---------------------------------------------------------------------------
# S1 weekly layout by offset from the long-run weekday (0 = long-run day).
# User-chosen long-run day: SOURCE: Daniels (2022), Ch. 8, Ch. 13, Ch. 16 (Table 16.2), page TBC [log 38].
# Default long-run day = race weekday: OWN DESIGN (A-43), see engine.generate_plan.
# Slot pattern per capacity (which offsets are LONG/HARD/EASY): SOURCE: TBC (not in the source map).
LAYOUT = {
    "Conservative": {0: "LONG", 3: "HARD", 5: "EASY"},
    "Standard": {0: "LONG", 2: "HARD", 4: "EASY", 5: "HARD"},
    "Progressive": {0: "LONG", 1: "EASY", 2: "HARD", 4: "EASY", 5: "HARD"},
}
# S2: at least 2 easy/rest days between hard sessions.
# SOURCE: Daniels (2022), Ch. 16 (novice and 2Q plans), page TBC [log 24].
S2_MIN_DAYS_BETWEEN_HARD = 2
# S2: no hard session on the day before or after the long run. OWN DESIGN (A-44)
S2_LONG_RUN_GAP_DAYS = 1
# Strides: 6 x 15-20 s on easy runs in base/hold weeks and on EASY + strides conversions.
# OWN DESIGN (A-14): 6 falls inside Daniels' 6-8.
STRIDES_COUNT = 6
STRIDES_DURATION_TEXT = "15-20 s"
# S3: easy runs aim for >= 30 min. SOURCE: Daniels (2022), Ch. 4 "Training Suggestions", page TBC [log 20].
EASY_RUN_MIN_MIN = 30.0
# S3/A-20: if remaining km per easy run < 1.0 km, convert the last hard session. OWN DESIGN (A-20)
EASY_RUN_MIN_KM_FOR_HARD = 1.0
# S4 main-set caps (Daniels M/T/I/R limits). SOURCE: Daniels (2022), Ch. 4 (M, T, I, R sections), page TBC [log 22].
S4_Z3_FRACTION = 0.20
S4_Z3_MAX_KM = 29.0
S4_Z3_MAX_MIN = 110.0
S4_Z4_FRACTION = 0.10
S4_Z5_INTERVAL_FRACTION = 0.08
S4_Z5_INTERVAL_MAX_KM = 10.0
S4_Z5_SHORT_FRACTION = 0.05
S4_Z5_SHORT_MAX_KM = 8.0
S4_Z5_SHORT_REP_MAX_S = 120.0  # Z5 rep <= 2 min = short reps; > 2 min = intervals
# S5 warm-up / cool-down (Z1): 10 min each below 30 km/week, else 15 min. OWN DESIGN (A-13)
WARMUP_THRESHOLD_KM = 30.0
WARMUP_MIN_LOW = 10.0
WARMUP_MIN_HIGH = 15.0
# S6 session-RPE load. SOURCE: Foster et al. (2001), Methods [log 4].
# LOAD_METHOD "session" (default) or "segment" (comparison only). OWN DESIGN (A-17)
LOAD_METHOD = "session"
LOAD_METHODS = ("session", "segment")
# S7 rep sizing: minimum 2 reps; halve the rep (round down to 100 m / 30 s) to a
# floor of 200 m / 1 min. OWN DESIGN (A-45, A-5)
S7_MIN_REPS = 2
S7_ROUND_M = 100.0
S7_ROUND_S = 30.0
S7_FLOOR_M = 200.0
S7_FLOOR_S = 60.0
# A-25: minimum continuous hard run (Z3 tempo, Z3 race pace, continuous Z4). OWN DESIGN (A-25)
MIN_CONTINUOUS_MIN = 10.0

# Session content (by track and PACU phase).
# Long-track sessions (run/walk in base, T reps 3/5 min, 20 min continuous T,
# race-pace run, 4 x 5 min T about 5 days out, 10 strides):
# SOURCE: Daniels (2022), Ch. 16, Table 16.2, page TBC [log 31].
LT_BUILD_REP_S_FIRST_HALF = 180.0
LT_BUILD_REP_S_SECOND_HALF = 300.0
LT_BUILD_JOG_S = 120.0
LT_BUILD_CONTINUOUS_MIN = 20.0
LT_BUILD_STRIDES = 10
LT_RACE_WEEK_REPS = 4
LT_RACE_WEEK_REP_S = 300.0
LT_RACE_WEEK_JOG_S = 120.0
# Long-track peak T reps 8 min (middle of 6-10 min) with 2 min jog. OWN DESIGN (A-14)
LT_PEAK_REP_S = 480.0
LT_PEAK_JOG_S = 120.0
# Short-track sessions. OWN DESIGN (A-46); direction supported by Campos et al. (2022),
# p. 311; Smyth et al. (2022), Fig. 1; Knopp et al. (2024), pp. 9, 11 [log 28-30].
# 10K peak 2 km reps with 2 min jog: OWN DESIGN (A-14).
ST_BUILD_REP_M = 1000.0
ST_BUILD_JOG_S = 120.0
ST_PEAK_5K_REP_M = 400.0
ST_PEAK_5K_JOG_S = 90.0
ST_PEAK_10K_REP_M = 2000.0
ST_PEAK_10K_JOG_S = 120.0
ST_RACE_WEEK_REP_M = 1000.0
ST_RACE_WEEK_JOG_S = 120.0
ST_RACE_WEEK_MIN_REPS = 2
# Race-week reps = this fraction of the last build-week Z4 reps (rounded half up),
# at least ST_RACE_WEEK_MIN_REPS. OWN DESIGN (A-21, A-22)
ST_RACE_WEEK_REP_FRACTION = 0.5

# Race week placement (A-7): hard session 4-6 days before the race, preferring 5;
# none in the 3 days before. OWN DESIGN (A-7)
RACE_WEEK_HARD_DAYS_BEFORE = (4, 5, 6)
RACE_WEEK_HARD_PREFERRED_DAYS_BEFORE = 5
RACE_WEEK_NO_HARD_WITHIN_DAYS = 3

# ---------------------------------------------------------------------------
# G rules: safety governor
# ---------------------------------------------------------------------------
# G2: ACWR threshold 1.5. SOURCE: Zhou & Zhou (2025), s. 4.1.3 [log 1].
ACWR_CAP = 1.5
# G1 chronic window (weeks), G6 cold start (4 baseline weeks at current km, Z2 RPE)
# and the G2 proportional cut with up to 10 iterations. OWN DESIGN (A-42)
CHRONIC_WINDOW_WEEKS = 4
BASELINE_WEEKS = 4
BASELINE_ZONE = "Z2"
G2_MAX_ITERATIONS = 10
# G2 factor. OWN DESIGN (A-49)
# "bisect" (default): one factor f per week, the largest f <= 1 for which the scaled
#   week (reps recomputed with S7) has ACWR <= 1.5, found by bisection. For a week with
#   no hard sessions this is exactly the brief's f = 1.5 x chronic / load.
# "literal": the brief's f = 1.5 x chronic / load, repeated up to G2_MAX_ITERATIONS.
#   Warm-up/cool-down are not scaled, so this only approaches 1.5 from above and often
#   ends in the A-27 last resort (kept for comparison).
G2_FACTOR_METHOD = "bisect"
G2_FACTOR_METHODS = ("bisect", "literal")
G2_BISECT_STEPS = 40
G2_MIN_FACTOR = 1e-3  # below this, scaling cannot reach the target: go to A-27
# G4 (governor runs last, trims only the actual week) and G5 (Component 3 targets
# pass through govern_week): SOURCE: Proposal s. 3.7.2, s. 3.7.3.

# ---------------------------------------------------------------------------
# Reporting (summary and persona report). OWN DESIGN (A-31)
# ---------------------------------------------------------------------------
# "Reached peak target" allows for output rounding (km are shown to 0.1).
REPORT_KM_TOLERANCE = 0.05
# Weekly-increase benchmark of 5-9%, report only. The brief attributes it to Knopp et al.
# (2024) but the source map has no verification-log row for it. SOURCE: TBC
KNOPP_WEEKLY_INCREASE_PCT = (5.0, 9.0)

# ---------------------------------------------------------------------------
# Numerical tolerances (implementation detail, not training rules). DEFINITION
# ---------------------------------------------------------------------------
ACWR_TOLERANCE = 1e-9  # ACWR <= cap + tolerance counts as within the cap
FLOAT_EPS = 1e-9  # guards floor() against 2.9999999 style float error


def with_overrides(**overrides: Any) -> SimpleNamespace:
    """Return a copy of this config with some constants replaced (for persona testing).

    Unknown names raise ``AttributeError`` so a typo cannot silently do nothing.
    """
    module = sys.modules[__name__]
    values = {k: v for k, v in vars(module).items() if k.isupper()}
    for key, value in overrides.items():
        if key not in values:
            raise AttributeError(f"Unknown config constant: {key}")
        values[key] = value
    if values["LOAD_METHOD"] not in values["LOAD_METHODS"]:
        raise ValueError(f"LOAD_METHOD must be one of {values['LOAD_METHODS']}")
    if values["G2_FACTOR_METHOD"] not in values["G2_FACTOR_METHODS"]:
        raise ValueError(f"G2_FACTOR_METHOD must be one of {values['G2_FACTOR_METHODS']}")
    return SimpleNamespace(**values)
