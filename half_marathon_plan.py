"""
Half Marathon - Full 12-Week Training Plan Generator
Run from the project root: python half_marathon_plan.py
"""

from src.component_1_prediction.predictor  import train_model, predict_marathon_time
from src.component_1_prediction.conversion  import convert_all_distances
from src.component_2_plan.fuzzy_engine      import compute_capacity, rpe_to_recovery_score
from src.component_2_plan.plan_generator    import generate_full_plan
from src.component_3_control.controller     import ProportionalController


# --- Runner profile ----------------------------------------------------------
# Edit these values to represent the actual runner.
RUNNER = {
    'vo2max':            50.0,   # mL/kg/min
    'weekly_mileage_km': 40.0,   # current weekly mileage
    'age':               28,
    'experience_months': 18,
    'long_run_km':       14.0,
    'resting_hr':        58,
    'rpe_last_session':  5,      # Borg CR10 (0=nothing, 10=max effort)
}


# --- Helpers -----------------------------------------------------------------

def fmt_time(minutes: float) -> str:
    h = int(minutes // 60)
    m = int(minutes % 60)
    s = int((minutes - int(minutes)) * 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _load_bar(load: float, max_load: float, width: int = 20) -> str:
    filled = int(round(load / max_load * width)) if max_load > 0 else 0
    return '#' * filled + '.' * (width - filled)


# --- Main --------------------------------------------------------------------

def main():
    SEP  = '=' * 70
    SEP2 = '-' * 70

    print(SEP)
    print('  HALF MARATHON - 12-WEEK TRAINING PLAN')
    print(SEP)
    print(f"  Runner : VO2max {RUNNER['vo2max']}  |  "
          f"{RUNNER['weekly_mileage_km']} km/wk  |  "
          f"age {RUNNER['age']}  |  "
          f"RPE last session {RUNNER['rpe_last_session']}/10")
    print()

    # --- Component 1: Predict goal time --------------------------------------
    print('  [Component 1] Predicting race times ...')
    model      = train_model()
    mara_time  = predict_marathon_time(model, RUNNER)
    all_times  = convert_all_distances(mara_time)
    half_time  = all_times['Half']

    print(f"  Predicted marathon time : {mara_time:.0f} min  ({fmt_time(mara_time)})")
    print(f"  Predicted half marathon : {half_time:.0f} min  ({fmt_time(half_time)})  <-- GOAL")
    print()

    # --- Component 2: Fuzzy capacity -> full plan ----------------------------
    recovery = rpe_to_recovery_score(RUNNER['rpe_last_session'])
    capacity = compute_capacity(RUNNER['weekly_mileage_km'], recovery)
    plan     = generate_full_plan(capacity, half_time)

    print(f"  [Component 2] Fuzzy capacity : {capacity:.1f}/100  "
          f"-> tier = {plan['capacity_label'].upper()}")
    print(f"  Recovery score (from RPE {RUNNER['rpe_last_session']}) : {recovery:.0f}/100")
    print()

    # --- Overview table ------------------------------------------------------
    loads    = [w['planned_load_au'] for w in plan['weeks']]
    max_load = max(loads)

    print(SEP)
    print(f"  {'Wk':>2}  {'Phase':<6}  {'Load (AU)':>9}  {'Volume bar':<22}  Key sessions")
    print(SEP2)

    for w in plan['weeks']:
        key = ', '.join(
            s['type'] for s in w['sessions']
            if s['type'] != 'Rest' and s['duration_min'] > 0
        )
        bar = _load_bar(w['planned_load_au'], max_load)
        print(f"  {w['week']:>2}  {w['phase']:<6}  {w['planned_load_au']:>9.0f}  "
              f"{bar}  {key}")

    print(SEP)
    print()

    # --- Week-by-week detail -------------------------------------------------
    print(SEP)
    print('  WEEK-BY-WEEK DETAIL')
    print(SEP)

    for w in plan['weeks']:
        race_week  = w['week'] == 12
        week_label = '  ** RACE WEEK **' if race_week else ''
        print()
        print(f"  -- Week {w['week']:>2}  [{w['phase']}]  "
              f"Load: {w['planned_load_au']:.0f} AU{week_label}")
        print(f"  {'Day':<11}  {'Session':<22}  {'Duration':>8}  {'RPE':>5}  {'Zone':>6}")
        print(f"  {'-'*11}  {'-'*22}  {'-'*8}  {'-'*5}  {'-'*6}")
        for s in w['sessions']:
            if s['type'] == 'Rest':
                print(f"  {s['day']:<11}  {'Rest':<22}  {'-':>8}  {'-':>5}  {'-':>6}")
            elif s['type'] == 'RACE DAY':
                print(f"  {s['day']:<11}  {'RACE DAY (21.1 km)':<22}  {'-':>8}  {'-':>5}  "
                      f"{s['zone']:>6}")
            else:
                dur = f"{s['duration_min']} min"
                print(f"  {s['day']:<11}  {s['type']:<22}  {dur:>8}  {s['rpe']:>5}  {s['zone']:>6}")

    print()
    print(SEP)
    print(f"  Goal: {fmt_time(half_time)}  |  "
          f"Tier: {plan['capacity_label'].upper()}  |  Capacity: {capacity:.1f}/100")
    print(SEP)
    print()

    # --- Component 3: Simulate first 3 weeks of feedback --------------------
    print(SEP)
    print('  [Component 3] Controller simulation -- first 3 weeks (K=0.5, ACWR cap=1.5)')
    print(SEP)

    controller = ProportionalController(K=0.5, acwr_cap=1.5)
    scenarios  = [
        ('Week 1', loads[0], 0.70),   # new plan, runner completes 70%
        ('Week 2', loads[1], 1.00),   # settles in, full completion
        ('Week 3', loads[2], 0.85),   # slightly under
    ]

    next_scale = 1.0
    print(f"  {'Week':<8}  {'Planned':>9}  {'Actual':>9}  "
          f"{'Done':>6}  {'Scale':>7}  {'Direction':>10}")
    print(f"  {'-'*8}  {'-'*9}  {'-'*9}  {'-'*6}  {'-'*7}  {'-'*10}")

    for label, base, pct in scenarios:
        planned    = base * next_scale
        actual     = planned * pct
        next_scale = controller.log_week(planned, actual)
        direction  = 'EASE' if next_scale < 0.99 else ('PROGRESS' if next_scale > 1.01 else 'HOLD')
        print(f"  {label:<8}  {planned:>9.0f}  {actual:>9.0f}  "
              f"{pct*100:>5.0f}%  {next_scale:>7.2f}  {direction:>10}")

    print()
    print('  scale < 1.0 = next week eased | scale > 1.0 = progressed | 1.0 = hold')
    print(SEP)


if __name__ == '__main__':
    main()
