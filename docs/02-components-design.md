# 02 — Components Design

This is the detailed design of the three components. Items marked **[Naji's own
design]** are original contributions and must never be presented as
literature-derived. Items marked **[OPEN]** are unresolved decisions.

---

## Component 1 — Race Time Prediction

**Goal:** predict a runner's finish time, then express it across the four race
distances (5K, 10K, 21.1K, 42.2K).

**Approach:** supervised ML **regression** on `train.csv`.

- **Label:** `actual_finish_time_minutes`.
- **Excluded as leakage:** `target_finish_time_minutes` (it is the runner's *goal*,
  is highly correlated with the outcome, and would not be a learned input). Other
  outcome-derived columns to review for leakage: `goal_completion_rate`,
  `medal_outcome`. See `docs/06-data-dictionary.md`.
- **Redundancy:** `weekly_mileage_km` and `weekly_mileage_miles` are the same
  quantity — keep one.
- **Strong legitimate predictors:** `personal_best_minutes`, `vo2_max`,
  `weekly_mileage_km`, `long_run_distance_km`, experience.

**Cross-distance conversion — [OPEN decision].** The dataset is marathon-only, so a
marathon prediction must be converted to the other distances. Two candidates:
- **Dash generalised approach** (`Win_Your_Race_Goal_...md`) — a generalised
  prediction-of-finish-time method.
- **Power-law baseline** (e.g. Riegel-style time–distance scaling) as the simpler
  fallback.
Decision still needs to be locked. Whichever is chosen, document the formula and
its source precisely.

**Honesty note:** because data is synthetic and marathon-only, frame this component
as a **methodological pipeline demonstration**, not a real-world accuracy claim.

### [OPEN] Inference-time feature gap
The model trains on a rich 41-column feature set, but a real user can only enter a
handful of markers (e.g. easy pace, HR). Decide explicitly how the deployed
predictor handles the features a user won't supply — a reduced-feature model,
sensible defaults/imputation, or a documented "demo uses full features" caveat.
This gap should be named in the thesis, not hidden.

---

## Component 2 — Training Plan Generation

A **rule-based engine** with a **fuzzy logic layer** on top, feeding a
**session-synthesis** stage.

### Fuzzy logic layer (Mamdani-style) **[Naji's own design for the MFs/rules]**
- **Inputs:** weekly mileage, and recovery score (0–100 scale).
- **Output:** a *capacity* value that drives **peak weekly volume** and the
  **weekly volume increase rate**.
- The membership functions, the rule base, and the conflict-resolution ordering
  are Naji's own design — cite the *use of fuzzy logic in training* (the
  `Running_Pace_Adjustment_..._Fuzzy_Logic...md` paper; and Huang & Wang, 2026,
  verified) as precedent for the technique, **not** for these specific rules.

### Intensity model
- **Five-zone HR/RPE intensity model**, anchored on **Knopp et al. (2024)** — the
  quantitative analysis of 92 sub-elite 12-week marathon plans, which provides
  evidence-based volume and intensity benchmarks for recreational runners.
- **Citation accuracy:** Knopp et al. **adapted** the five-zone model from
  **Jamnick et al.** and **Seiler** — do **not** credit Knopp as the originator of
  the zone framework. (Confirmed in the paper's Table 2 and methods.)

### Session synthesis
- Maps (weekly volume + training phase) → **named workouts** (e.g. long run, tempo,
  intervals, easy/recovery), each tagged to a target zone. The rep structures are
  **[Naji's own design]**.

### Recovery score source
- **Primary:** self-report wellness check.
- **Alternative:** a computed composite from objective markers (e.g. sleep, RHR,
  recovery_score field).

### Calendar placement — [scope decision]
- **FYP-scoped implementation:** **fixed** placement with a fallback rule.
- **Target / future work:** adaptive placement. Defended with a prepared viva
  script (see `docs/03-decisions-and-scope.md`).

---

## Component 3 — Closed-Loop Plan Adjustment

**Core deliverable:** a **Proportional Controller (PC)**.
**Time-permitting enhancement:** a **Fuzzy Feedback Controller**.
**Stretch / future work:** a **Differential Evolution** controller (demoted).

### Load currency
- **session-RPE** = Borg CR10 rating × session duration in minutes, summed across
  the week into **arbitrary units (AU)**. This is the load signal the controller
  acts on.

### Control logic
- Each week, the controller compares logged load against the plan and outputs a
  scaling signal for the next week.
- **Adjustment polarity: easing.** Skipping sessions → an **easier** next week.
  **[Naji's own design]** — this is deliberately *different* from Connor et al.'s
  *make-up* polarity (where missed load is added back). The choice of polarity and
  the **gain K** are Naji's contributions.
- **Architecture precedent:** Connor et al. (2022) for the closed-loop controller
  architecture — cite for the *architecture*, not for the easing polarity.

### Safety constraint
- **ACWR (acute:chronic workload ratio) cap of 1.5** limits how fast load can ramp.
- **Sourcing:** the 1.5 cap is taken via **Zhou & Zhou (2025)**. **Gabbett (2016)**
  is the conceptual origin of the ACWR injury-risk idea **but must be verified
  against the primary paper before being cited for the 1.5 figure** — Gabbett
  (2016) appears in the corpus only inside other papers' reference lists, not as a
  readable source. See `docs/04-citations-and-sources.md`.
- **Critique to acknowledge:** Bornn, Ward & Norman (2019) argue training schedule
  confounds the ACWR–injury relationship. Chapter 4 should frame the 1.5 ceiling
  as a **heuristic**, citing this critique honestly.

### Deferred justification
- The specific **K gain value** and the **ACWR ceiling rationale** are justified in
  **Chapter 4**, not Chapter 3.
