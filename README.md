# PACU: Personalized Adaptive Coach for U

Final-year project (UiTM): *Adaptive Training Plan Recommendation and Race Time
Prediction for Distance Runners Using Machine Learning.*

| Component | What it does | Where |
|---|---|---|
| 1. Race time prediction | ML regression on a synthetic marathon dataset, with Riegel conversion to 5K/10K/HM | `notebooks/`, `src/pipeline.py` |
| 2. Training plan engine | Staged crisp IF-THEN rule engine: inputs to a dated, periodised plan | `pacu/component2/` |
| 3. Closed-loop adjustment | Weekly feedback controller (not built yet) | n/a |

Project notes for contributors are in `CLAUDE.md` and `docs/`.

## Component 2: rule-based training plan engine

Component 2 turns a runner's inputs into a week-by-week plan. It uses no ML, no fuzzy
logic and no randomness, so the same inputs always give the same plan. Every week and
every session lists the rule IDs that produced it (`rule_trace`). Every number lives in
`pacu/component2/config.py`, tagged with its rule ID and source. Own-design choices are
listed in [ASSUMPTIONS.md](ASSUMPTIONS.md).

### How to run

Use Python 3.11+ (the project uses the Anaconda Python 3.12 install). Component 2 needs
only the standard library; the tests need `pytest`. Run from the project root:

```bash
python -m pytest -q                                   # all tests
python scripts/persona_report.py                      # persona report -> reports/
python -m pacu.component2 --input reports/inputs/P03.json --pretty            # text table
python -m pacu.component2 --input my_runner.json --out plan.json               # JSON plan
python -m pacu.component2 --input my_runner.json --pretty --load-method segment
```

### Inputs (`PlanInputs`, JSON)

| Field | Type | Notes |
|---|---|---|
| `target_distance` | `"5K"`, `"10K"`, `"HM"`, `"M"` | |
| `predicted_times_s` | object with all four distances | from Component 1; seconds or `"h:mm:ss"` |
| `easy_pace_s_per_km` | number or `"m:ss"` | |
| `current_weekly_km` | number | |
| `recovery_answers` | `[q1, q2, q3]`, each 1-5 | sleep, muscle recovery, freshness (5 = best) |
| `injury_flag` | bool | pauses all hard sessions (A-9) |
| `race_date`, `start_date` | ISO date | `start_date` defaults to today |
| `long_run_weekday` | 0-6 (Mon = 0) or null | null = race weekday |
| `max_hr` | int or null | heart-rate ranges only if given |
| `override_entry_minimum` | bool | see V4 |

Example: any file in `reports/inputs/`.

### Outputs (`PlanResult`, JSON)

- **Plan:** `status` (`OK` or `BELOW_ENTRY_MINIMUM`), `warnings`, `notes`, `advisories`,
  `suggestions`, an echo of the inputs, `recovery_score`, `capacity` and the C rule that
  fired, `track`, `N`, `hold_weeks`, `phase_lengths`, `race` (reported separately),
  `summary`, `weeks`.
- **Week:** `label`, dates, `daniels_phase`, `pacu_phase`, `week_type`, `level_km`
  (planned) and `km` (actual), `easy_share`, `load`, `chronic_load`, `acwr`, `governor`
  (fired, factor), `rule_trace`, `notes`, `sessions`.
- **Session:** `date`, `slot` (LONG / HARD / EASY / RACE), `title` (e.g.
  `"6 × 400 m @ 5:42/km, 90 s jog"`), `main_zone`, `segments` (warm-up, reps, jogs,
  steady, cool-down), `reps`, `rep_length`, `km`, `minutes`, `target_rpe`, `load`,
  `hr_range`, `strides`, `run_walk_ok`, `rule_trace`, `notes`.

Dates are ISO strings and paces are `"m:ss/km"`. Values are rounded only at output:
km to 0.1, minutes to whole numbers.

### Rule families

| Family | What it decides | Module |
|---|---|---|
| Z | Five intensity zones: HR %, RPE, pace targets, load RPE | `zones.py` |
| C | Recovery score and capacity (Conservative / Standard / Progressive), rules C1-C4 by priority | `capacity.py` |
| P | Plan length (P1, P2), Daniels Fig. 10.2 phases (P3), recovery weeks (P4), easy-share targets (P5-P7) | `plan_calendar.py`, `phases.py` |
| V | Weekly volume: start level, 3-week holds and steps, peak cap, entry minimum | `volume.py` |
| L | Long-run length caps | `long_run.py` |
| T | Taper length and volume | `phases.py`, `taper.py` |
| S | Weekly layout, spacing, session content, main-set caps and sizing, easy runs, load | `sessions.py`, `load.py` |
| G | ACWR safety governor (ACWR ≤ 1.5), runs last for every week | `governor.py` |

`engine.py` runs them in the order of the build brief, section 5. `serialize.py` and
`__main__.py` handle JSON and the CLI.

### Functions for Component 3

```python
from pacu.component2 import govern_week, make_recovery_week, change_long_run_day, clear_injury_flag
```

- `govern_week(week, previous_loads, config)`: G1-G3 on one week; Component 3's targets must pass through it.
- `make_recovery_week(plan, week_label)`: turn a future week into a recovery week, then re-govern the later weeks.
- `change_long_run_day(plan, new_weekday, from_week_label)`: re-lay the plan from that week onward.
- `clear_injury_flag(plan, from_week_label)`: bring hard sessions back from that week onward.

Each returns a new `PlanResult` (the original is not changed), except `govern_week`,
which changes the week in place.

### Tuning and evaluation

Edit `config.py`, re-run `python scripts/persona_report.py`, and compare
`reports/persona_report.md`. The report covers 14 personas, a comparison of the two load
methods, a comparison of the two G2 factor methods, and the P04/P05 cliff-edge
comparison. `tests/test_personas.py` checks every week of every persona against the
safety and structure rules.
