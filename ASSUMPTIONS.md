# Component 2: own-design assumptions (A-n)

Every own-design choice in `components/component2/` is listed here with its code
location. In code, each one carries a comment `# OWN DESIGN (A-n)`; search for
that string to find it. Numbers live in `components/component2/config.py` under the named
constants.

These are **Naji's own design** (or, for A-48 and A-49, implementation decisions
taken during the build). They are not literature-derived and must not be presented as
such in the thesis.

**Origin** column:
- *Brief §8*: listed in the build brief.
- *Gap n*: a gap found while planning the build; Naji approved the proposed fix on 13 Nov 2026.
- *Source map*: marked OWN DESIGN in the source map (verification log, 11-13 Nov 2026).
- *Build*: a decision taken during implementation, flagged to Naji for review.

| ID | Assumption | Origin | Code location |
|---|---|---|---|
| A-1 | PACU phase mapping: Daniels Phase I = base, II = build, III = peak, IV = peak except its last T1 weeks = taper. | Brief §8 | `phases.py: plan_phases`; config `PACU_PHASE_OF_DANIELS` |
| A-2 | Base phase has 0 hard sessions for every capacity (the optional short Z3 in 5K/10K base is not used). | Brief §8 | `sessions.py: hard_needed` |
| A-3 | Non-race taper weeks keep the capacity's hard-session count (T3); race week has exactly 1. | Brief §8 | `sessions.py: hard_needed`; config `RACE_WEEK_HARD_SESSIONS` |
| A-4 | The race is excluded from week km, easy share, load and ACWR, and reported separately. | Brief §8 | `load.py: session_load, refresh_totals`; `sessions.py: new_race`; `engine.py: generate_plan` (`plan.race`) |
| A-5 | When the 2-rep minimum conflicts with the S4 cap, the cap wins: halve the rep, otherwise EASY + strides (`HARD_SESSION_TOO_SMALL`). | Brief §8 | `sessions.py: size_main_set, build_week`; config `S7_*` |
| A-6 | If current km ≥ the peak target, hold current km (no cut, no steps); note `ABOVE_PEAK_TARGET`. | Brief §8 | `volume.py: weekly_levels` |
| A-7 | Weeks end on race day; leftover 0-6 days before week 1 are unscheduled. Race week: no hard session within 3 days of the race, the single hard session 4-6 days out (prefer 5); no long run when its weekday differs from the race weekday. | Brief §8 | `plan_calendar.py: plan_calendar`; `sessions.py: build_week`; config `RACE_WEEK_*` |
| A-8 | The taper reference ("the week before" the first taper week) is the last non-recovery, non-taper week's level. | Brief §8 | `taper.py: taper_reference_index` |
| A-9 | **Revised 13 Nov 2026 (replaces the brief's A-9).** If `injury_flag` is true, every HARD slot becomes EASY in all weeks (strides only in base and hold weeks). Advisory: "Hard sessions are paused while you report an injury or illness. Please see a doctor or physiotherapist. They will be added back when your weekly check-in is clear." `clear_injury_flag(plan, from_week_label)` rebuilds hard sessions from that week and re-governs in order. | Naji's reply | `engine.py: generate_plan` (`INJURY_ADVISORY`, `hard_paused`), `clear_injury_flag`; `sessions.py: hard_needed, build_week` |
| A-10 | No marathon-pace segments inside long runs in v1 (one steady Z2 block). | Brief §8 | `sessions.py: new_long` |
| A-11 | Below the entry minimum, no plan is generated unless `override_entry_minimum` is set and current km > 0. | Brief §8 | `engine.py: generate_plan`; `volume.py: entry_suggestions` |
| A-12 | Short-track Z3 tempo pace = midpoint of predicted marathon and HM pace. Long-track race-pace run = marathon pace (M) or HM pace (HM). | Brief §8 | `zones.py: build_paces` |
| A-13 | Warm-up and cool-down are 10 min each if week km < 30, otherwise 15 min each. | Brief §8 | `sessions.py: warmup_minutes`; config `WARMUP_*` |
| A-14 | Long-track peak T reps are 8 min with 2 min jog; 10K peak 2 km reps use a 2 min jog; 6 strides (within Daniels' 6-8). | Brief §8 | config `LT_PEAK_*`, `ST_PEAK_10K_*`, `STRIDES_COUNT`; `sessions.py: make_main_set, add_strides` |
| A-15 | The long run = the maximum allowed by L1 and L2. | Brief §8 | `long_run.py: long_run_km` |
| A-16 | Conservative alternation order: short-track build starts with Z4 reps; long-track peak starts with the race-pace run. | Brief §8 | `sessions.py: select_workouts` |
| A-17 | Load method defaults to session-RPE (`"session"`); `"segment"` is kept for comparison. | Brief §8 | config `LOAD_METHOD`; `load.py: session_load` |
| A-18 | Hold weeks (beyond 24 weeks) are all easy at current km, have no recovery weeks, and count in the ACWR history. | Brief §8 | `plan_calendar.py: plan_calendar`; `engine.py: generate_plan`; `sessions.py: hard_needed` |
| A-19 | The P5 hard budget is split evenly across the week's hard sessions. | Brief §8 | `sessions.py: build_week` |
| A-20 | If remaining km per easy run is < 1.0 km, the last hard session becomes EASY + strides (`VOLUME_TOO_LOW_FOR_HARD`). | Brief §8 | `sessions.py: build_week`; config `EASY_RUN_MIN_KM_FOR_HARD` |
| A-21 | Race-week sessions (short: reps of 1 km; long: 4 × 5 min) are a target. Allowance = min(target, S4 cap, P5 budget), then normal S7 sizing (cap wins, as A-5). | Gap 1 | `sessions.py: make_main_set` (`ST_RACE_WEEK`, `LT_RACE_WEEK`), `main_set_allowance` |
| A-22 | "Last build-week reps" = reps of the most recent build week that actually had Z4 1 km reps; if none, 2. | Gap 2 | `sessions.py: last_build_z4_reps` |
| A-23 | Conservative alternation counts only weeks that call for a hard session (recovery weeks skipped). Long track continues the same sequence into non-race taper weeks. Counted on the planned weeks, before S7/G2 conversions. | Gap 3 | `sessions.py: alternation_index` |
| A-24 | Long-track build: the first floor(B/2) build weeks use 3 min reps, the rest 5 min; the 20 min continuous rule applies to the last build week that has hard sessions (5 min reps if the allowance is too small). | Gap 4 | `sessions.py: _lt_build_code, make_main_set` |
| A-25 | Minimum continuous hard run (Z3 tempo, Z3 race pace, continuous Z4) is 10 min; below that, EASY + strides with `HARD_SESSION_TOO_SMALL`. | Gap 5 (value from Naji) | config `MIN_CONTINUOUS_MIN`; `sessions.py: size_main_set` |
| A-26 | After `change_long_run_day`, any HARD session in the first re-laid week that breaks S2 against the previous week becomes EASY + strides (`S2_TRANSITION`). If last week's hard session falls the day before the new long run, it cannot be moved (already scheduled), so the week gets note `S2_TRANSITION_UNRESOLVED`. | Gap 6 | `sessions.py: _apply_s2_transition`; `engine.py: change_long_run_day` |
| A-27 | G2 last resort: convert hard sessions to EASY one at a time, latest first; their km rejoins the S3 split; then rescale. | Gap 7 | `governor.py: _convert_latest_hard, govern_week` |
| A-28 | A plan needs at least 2 whole weeks (error otherwise); taper length = min(T1, N − 1); taper/race overrides any phase for tiny N. | Gap 8 | config `MIN_PLAN_WEEKS`; `plan_calendar.py: plan_calendar`; `phases.py: taper_length, plan_phases` |
| A-29 | The RACE session replaces whatever slot falls on race day. | Gap 9 | `sessions.py: build_week, new_race` |
| A-30 | `make_recovery_week`: level = 80% of the previous week's planned level; later weeks keep their levels (G4) but are rebuilt and re-governed in order; taper and race weeks are rejected. | Gap 10 | `engine.py: make_recovery_week` |
| A-31 | Report definitions: peak km reached = highest post-governor km of non-taper weeks; "reached target" compares it with the peak target (0.05 km tolerance); plan easy share (P7) = easy km / total km over plan weeks 1..N; build increase = mean % change of actual km for non-recovery build weeks, each against the previous non-recovery plan week. | Gap 11 | `engine.py: summarize`; `scripts/persona_report.py`; config `REPORT_KM_TOLERANCE` |
| A-32 | Week note `LONG_RUN_NOT_LONGEST` when an easy run is longer than the long run (L1's 30% cap with 3 runs a week); counted in the persona report. | Naji's reply | `sessions.py: refresh_week` |
| A-33 | Zone pace targets (Z1 = easy + 30 s/km, Z2 = easy, Z4 = predicted 10K pace, Z5 = predicted 5K pace) and the load RPE values 1.5/3.5/5.5/7.5/9.5 (CR10 range midpoints). | Source map | config `ZONE_LOAD_RPE`, `Z1_PACE_OFFSET_S_PER_KM`, `Z4_PACE_DISTANCE`, `Z5_PACE_DISTANCE`; `zones.py: build_paces` |
| A-34 | Capacity bands (mileage < 20 / 20-40 / > 40 km; recovery 3-7 / 8-11 / 12-15), rules C1-C4 and their priority order. | Source map | `capacity.py`; config `MILEAGE_*`, `RECOVERY_*`, `C_RULE_PRIORITY` |
| A-35 | V1 (week 1 = current km), V3 (cap and hold at the peak target), V4 (entry check) and the entry minimums 5/10/15/25 km. | Source map | `volume.py`; config `ENTRY_MIN_KM` |
| A-36 | Peak targets, all cells except marathon Standard 58 and Progressive 75 (Knopp et al., 2024). | Source map | config `PEAK_TARGET_KM` |
| A-37 | L2 caps for 5K (12 km), 10K (16 km) and HM (20 km). | Source map | config `L2_CAP_KM` |
| A-38 | T1 taper of 1 week for 5K and 10K. | Source map | config `TAPER_WEEKS` |
| A-39 | T2 cut of 25% per non-race taper week (inside Knopp et al.'s 22-31%). | Source map | config `TAPER_WEEK_FRACTION` |
| A-40 | P4 recovery week at 80% of the previous week's planned level. | Source map | config `RECOVERY_WEEK_FRACTION`; `volume.py: weekly_levels` |
| A-41 | P5 easy-share targets by phase: I ≥ 90%, II 80%, III 75%, IV 80%. | Source map | config `EASY_SHARE_TARGET`; `phases.py: easy_share_target` |
| A-42 | G1 4-week chronic window, G6 cold start (4 baseline weeks at current km × easy pace × 3.5), G2 proportional cut with up to 10 iterations. | Source map | config `CHRONIC_WINDOW_WEEKS`, `BASELINE_*`, `G2_MAX_ITERATIONS`; `load.py: baseline_load`; `governor.py` |
| A-43 | Default long-run day = race weekday. | Source map | `engine.py: generate_plan` |
| A-44 | S2: no hard session the day before or after the long run. | Source map | config `S2_LONG_RUN_GAP_DAYS`; `sessions.py: s2_violations` |
| A-45 | S7 rep sizing: minimum 2 reps; halve the rep (round down to 100 m / 30 s) to a floor of 200 m / 1 min. | Source map | config `S7_*`; `sessions.py: size_main_set, halve_rep` |
| A-46 | Short-track session content (build Z4 1 km reps + Z3 tempo, peak Z5 400 m / Z4 2 km reps, race-week 1 km reps). Direction supported by Campos et al. (2022), p. 311; Smyth et al. (2022), Fig. 1; Knopp et al. (2024), pp. 9, 11. | Source map | config `ST_*`; `sessions.py: select_workouts, make_main_set` |
| A-47 | P2 minimum plan length of 6 weeks (5K/10K) and 9 weeks (HM), an own rule built on Daniels (2022), Fig. 10.2. | Source map | config `MIN_WEEKS` |
| A-48 | G2 scales each hard session's main-set **allowance** by f, then S7 re-derives whole reps (rather than scaling the rounded reps, which would lose a rep on every cut). G3 also re-checks **L1** and **S4** against the actual (cut) week km: long-run excess moves to the easy runs (same Z2 load, same km); a main set over its S4 cap is re-sized down. | Build | `sessions.py: main_set_allowance`; `governor.py: _scale_week, _g3_s4, _g3_long_run` |
| A-49 | **G2 factor by bisection.** The brief's f = 1.5 × chronic ÷ load assumes the whole week scales, but warm-up and cool-down never scale and reps change in whole steps. So the brief's iteration only approaches 1.5 from above, runs out of its 10 iterations, and the A-27 last resort then converts a hard session over a residual as small as 0.0001 ACWR (14 conversions across the personas). The default uses the **largest single f ≤ 1** for which the scaled week has ACWR ≤ 1.5. For a week with no hard sessions this equals the brief's formula exactly (the G2 worked check is unchanged). The literal formula is kept as `G2_FACTOR_METHOD = "literal"`. | Build | `governor.py: g2_factor`; config `G2_FACTOR_METHOD`, `G2_BISECT_STEPS`, `G2_MIN_FACTOR` |

## Values tagged `SOURCE: TBC` (not covered by the source map)

| Value | Where | Note |
|---|---|---|
| S1 slot pattern per capacity (which offsets are LONG / HARD / EASY) | config `LAYOUT` | The brief gives the table; the source map covers only the user-chosen day and the race-weekday default. |
| 5-9% weekly-increase benchmark | config `KNOPP_WEEKLY_INCREASE_PCT` | The brief attributes it to Knopp et al. (2024); there is no verification-log row for it. Report only. |

## Source-map rows not implemented in Component 2

- **"S1: Sunday fallback" (Daniels, 2022, Ch. 10).** The brief has no Sunday fallback rule (`long_run_weekday = None` falls back to the race weekday, A-43), so none is implemented.
- **"Missed-session priority" (Daniels, 2022, Ch. 10).** This is a Component 3 hook; Component 3 is not built yet.

## Secondary citations

Bosquet et al. (2007), Midgley et al. (2007) and Boullosa et al. (2020) are reached only
through Knopp et al. (2024). Cite them as secondary ("as cited in Knopp et al., 2024")
and never put them in the reference list.
