# 06 — Data Dictionary (`train.csv`)

**Source:** Kaggle. **Synthetic. Marathon-only.** ~80,000 rows, 41 columns.
**Label for Component 1:** `actual_finish_time_minutes`.

This honesty matters: any accuracy reported is a demonstration of the **pipeline**,
not a claim about real runners.

## Columns

### Identifier / drop
- `runner_id` (str) — drop from modelling.

### Demographics & profile
- `age` (int)
- `gender` (str, categorical)
- `bmi` (float)
- `running_experience_months` (int)
- `previous_marathon_count` (int)
- `training_program` (str, categorical)
- `motivation_level` (int)
- `mental_preparation_score` (int)

### Fitness / performance markers (strong legitimate predictors)
- `personal_best_minutes` (float) — strong predictor
- `vo2_max` (float) — strong predictor
- `resting_heart_rate_bpm` (int)

### Training volume & structure
- `weekly_mileage_km` (float) — **keep this one**
- `weekly_mileage_miles` (float) — **redundant** with km; drop one to avoid collinearity
- `runs_per_week` (int)
- `long_run_distance_km` (float)
- `speed_work_sessions_per_week` (int)
- `rest_days_per_week` (int)
- `cross_training_hours_per_week` (float)
- `early_morning_run_frequency` (int)
- `run_club_attendance_rate` (int)

### Adherence & consistency
- `training_adherence_pct` (int)
- `consecutive_weeks_no_miss` (int)
- `training_streak_days` (int)
- `missed_workout_pct` (int)
- `warmup_adherence_pct` (int)
- `stretching_adherence_pct` (int)
- `weather_condition_training_pct` (int)

### Recovery / lifestyle
- `recovery_score` (float) — **also a Component 2 fuzzy input** (0–100 scale)
- `sleep_hours_avg` (float)
- `nutrition_score` (float)
- `hydration_consistency` (float)
- `injury_count` (int)
- `injury_severity` (str, categorical)

### Race-day context
- `marathon_date` (str) — temporal; likely drop for prediction
- `marathon_weather` (str, categorical) — only known near/at race day; decide if it
  belongs in a *pre-race* predictor
- `course_difficulty` (str, categorical) — known in advance; usable

### Target & leakage
- `actual_finish_time_minutes` (float) — **LABEL** (predict this)
- `target_finish_time_minutes` (int) — **EXCLUDE (leakage):** the runner's *goal*,
  highly correlated with outcome, not a learned input
- `goal_completion_rate` (int) — **review for leakage:** outcome-derived
- `medal_outcome` (int) — **review for leakage:** determined by the finish result

## Modelling checklist

1. Drop `runner_id`.
2. Drop `target_finish_time_minutes` (leakage). Review and likely drop
   `goal_completion_rate`, `medal_outcome`.
3. Drop one of the two mileage columns.
4. Decide handling of race-day context (`marathon_weather`, `marathon_date`,
   `course_difficulty`) for a pre-race predictor.
5. Encode categoricals (`gender`, `training_program`, `injury_severity`,
   `course_difficulty`, `marathon_weather`).
6. Train regression → predict `actual_finish_time_minutes` → convert across
   distances (method = [OPEN], see Component 1).
