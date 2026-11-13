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

A **staged crisp rule-based engine**: IF-THEN rules only, with no fuzzy logic, no ML and
no randomness, so it is deterministic. It is implemented in `pacu/component2/` (see
`README.md`). Every week and every session lists the IDs of the rules that produced it
(`rule_trace`). Rule families: Z (zones), C (capacity), P (plan length and phases),
V (volume), L (long run), T (taper), S (sessions), G (ACWR governor). Every number is
in `pacu/component2/config.py` with its source tag. Every own-design choice is in
`ASSUMPTIONS.md` (A-1 to A-49).

**Changed Nov 2026 (D9):** the capacity layer was a Mamdani fuzzy layer; it is now
crisp rules C1–C4. Fuzzy smoothing of the band edges is future work only.

### Capacity layer (crisp rules C1–C4) **[Naji's own design: bands, rules, priority]**
- **Inputs:** current weekly mileage (bands < 20 / 20–40 / > 40 km) and a recovery
  score from three self-report questions (sleep, muscle recovery, freshness; each 1–5;
  sum 3–15; bands 3–7 / 8–11 / 12–15).
- **Rules, lowest priority number wins:** C1 recovery Low → Conservative;
  C2 mileage Low → Conservative; C3 mileage High AND recovery High → Progressive;
  C4 otherwise → Standard. Capacity is fixed for the whole plan.
- **Capacity sets:** runs per week (3/4/5), hard sessions per week (1/2/2), the weekly
  volume step (1.6 km × runs) and the peak target.
- **Sourced parts:** the question set and 1–5 scale (Daniels, 2022, Table 2.1;
  Goldberg et al., 2025; Smyth et al., 2022), runs per week and hard sessions per week
  (Daniels, 2022, Ch. 16; Knopp et al., 2024). The bands, cut-offs, rules and priority
  order are own design. Full source map: `docs/04-citations-and-sources.md`.

### Intensity model
- **Five-zone HR/RPE intensity model**, anchored on **Knopp et al. (2024)**, the
  quantitative analysis of 92 sub-elite 12-week marathon plans, which provides
  evidence-based volume and intensity benchmarks for recreational runners.
- **Citation accuracy:** Knopp et al. **adapted** the five-zone model from
  **Jamnick et al.** and **Seiler**. Do **not** credit Knopp as the originator of the
  zone framework (confirmed in the paper's Table 2 and methods).
- Zone paces come from the runner's easy pace and Component 1's predicted paces (no
  VDOT, D2). The pace targets and load RPE values are own design (A-12, A-33).

### Periodisation, volume, taper
- Phase allocation from Daniels (2022), Fig. 10.2, mapped to base / build / peak /
  taper (A-1). Volume is held for 3 weeks, then a recovery week, then stepped up, and
  never exceeds the peak target. Long-run caps (L1, L2). Taper of 1/1/2/3 weeks
  (5K/10K/HM/M).

### Session synthesis
- Maps week volume + phase → named workouts on a fixed weekly layout around the
  long-run day: long run, easy runs, and hard sessions (threshold reps, tempo, race
  pace, intervals). Main-set caps follow Daniels (2022) Ch. 4. Long-track content
  follows Daniels (2022) Table 16.2. Short-track content and the rep sizing rules are
  **[Naji's own design]** (A-45, A-46).

### Safety governor
- Weekly **ACWR ≤ 1.5** (Zhou & Zhou, 2025), applied last to every week. A week above
  the cap is scaled down; the cut trims only that week. The way the cut factor is
  computed (A-49, bisection) is an implementation decision awaiting Naji's confirmation.

### Recovery score source
- **Primary (built):** the three-question self-report above.
- **Alternative:** a computed composite from objective markers (e.g. sleep, RHR,
  recovery_score field), D8.

### Calendar placement — [scope decision]
- **FYP-scoped implementation:** **fixed** weekly layout relative to a user-chosen
  long-run day (default: the race weekday). Component 3 can move the long-run day
  mid-plan with `change_long_run_day`.
- **Target / future work:** adaptive placement. Defended with a prepared viva
  script (see `docs/03-decisions-and-scope.md`).

---

## Component 3 — Closed-Loop Plan Adjustment

**Core deliverable:** a **Proportional Controller (PC)**.
**Fuzzy Feedback Controller:** future work only (Nov 2026; fuzzy logic is not used anywhere in the build, D9).
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

### Hooks provided by Component 2
- `govern_week` (every Component 3 target passes the ACWR governor), `make_recovery_week`
  (when the weekly recovery score is Low, 3–7), `change_long_run_day`,
  `clear_injury_flag`. See `README.md`.

### Deferred justification
- The specific **K gain value** and the **ACWR ceiling rationale** are justified in
  **Chapter 4**, not Chapter 3.
