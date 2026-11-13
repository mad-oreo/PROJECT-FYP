"""
FYP Demo — Adaptive Training Plan System
Feasibility test: all three components running end-to-end on synthetic data.
Run from the project root: python demo.py
"""

from src.component_1_prediction.predictor  import train_model, predict_marathon_time
from src.component_1_prediction.conversion  import convert_all_distances
from src.component_2_plan.fuzzy_engine      import compute_capacity, rpe_to_recovery_score
from src.component_2_plan.plan_generator    import generate_plan
from src.component_3_control.controller     import ProportionalController


def fmt_time(minutes: float) -> str:
    h   = int(minutes // 60)
    m   = int(minutes % 60)
    s   = int((minutes - int(minutes)) * 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def run_demo():
    SEP = "=" * 60

    # ------------------------------------------------------------------ #
    # User inputs (hardcoded for demo)                                     #
    # ------------------------------------------------------------------ #
    user = {
        'vo2max':            48.0,   # mL/kg/min
        'weekly_mileage_km': 45.0,   # km/week
        'age':               30,
        'experience_months': 24,
        'long_run_km':       16.0,   # km
        'resting_hr':        60,     # bpm
        'rpe_last_session':  6,      # Borg CR10 (0-10)
    }
    target_distance = '10K'

    print(SEP)
    print("  FYP DEMO — Adaptive Training Plan System")
    print(SEP)
    print(f"  VO2max={user['vo2max']}  |  mileage={user['weekly_mileage_km']}km/wk  "
          f"|  age={user['age']}  |  target={target_distance}")
    print()

    # ------------------------------------------------------------------ #
    # Component 1 — Race Time Prediction + Cross-Distance Conversion       #
    # ------------------------------------------------------------------ #
    print(SEP)
    print("  COMPONENT 1 — Race Time Prediction")
    print(SEP)
    model         = train_model()
    marathon_time = predict_marathon_time(model, user)
    all_times     = convert_all_distances(marathon_time)

    print(f"  Predicted marathon time : {marathon_time:.1f} min  ({fmt_time(marathon_time)})")
    print()
    print("  Cross-distance predictions (Riegel/Dash proxy):")
    for dist, t in all_times.items():
        print(f"    {dist:10s}  {t:6.1f} min   ({fmt_time(t)})")
    print()

    # ------------------------------------------------------------------ #
    # Component 2 — Training Plan Generation                               #
    # ------------------------------------------------------------------ #
    print(SEP)
    print("  COMPONENT 2 — Training Plan Generation")
    print(SEP)

    recovery_score = rpe_to_recovery_score(user['rpe_last_session'])
    capacity       = compute_capacity(user['weekly_mileage_km'], recovery_score)

    print(f"  RPE last session : {user['rpe_last_session']}/10")
    print(f"  Recovery score   : {recovery_score:.0f}/100  (derived from RPE)")
    print(f"  Fuzzy capacity   : {capacity:.1f}/100")
    print()

    plan   = generate_plan(target_distance, capacity, all_times[target_distance])
    week_1 = plan['week_1']

    print(f"  Plan: {plan['num_weeks']}-week {target_distance} programme  |  "
          f"Goal time: {fmt_time(plan['predicted_goal_time_min'])}  |  "
          f"Week 1 phase: {week_1['phase']}  |  "
          f"Capacity tier: {week_1['capacity_label'].upper()}")
    print()
    print(f"  {'Day':<12}  {'Session':<20}  {'Duration':>8}  {'Zone':>6}  {'Load (AU)':>10}")
    print(f"  {'-'*12}  {'-'*20}  {'-'*8}  {'-'*6}  {'-'*10}")
    for s in week_1['sessions']:
        load_str = f"{s['rpe'] * s['duration_min']}" if s['rpe'] > 0 else "-"
        dur_str  = f"{s['duration_min']} min" if s['duration_min'] > 0 else "-"
        print(f"  {s['day']:<12}  {s['type']:<20}  {dur_str:>8}  {s['zone']:>6}  {load_str:>10}")
    print(f"\n  Week 1 total planned load: {week_1['planned_load_au']:.0f} AU")
    print()

    # ------------------------------------------------------------------ #
    # Component 3 — Closed-Loop Adjustment (3-week simulation)             #
    # ------------------------------------------------------------------ #
    print(SEP)
    print("  COMPONENT 3 — Closed-Loop Adjustment (K=0.5, ACWR cap=1.5)")
    print(SEP)

    controller   = ProportionalController(K=0.5, acwr_cap=1.5)
    base_load    = week_1['planned_load_au']
    next_scale   = 1.0

    # Simulate three weeks with different completion rates
    scenarios = [
        ("Week 1", 0.65),   # missed ~35% — had a bad week
        ("Week 2", 1.00),   # completed everything
        ("Week 3", 0.90),   # slightly under
    ]

    print(f"  {'Week':<8}  {'Planned (AU)':>13}  {'Actual (AU)':>12}  "
          f"{'Completion':>11}  {'Next scale':>11}  {'Direction':>10}")
    print(f"  {'-'*8}  {'-'*13}  {'-'*12}  {'-'*11}  {'-'*11}  {'-'*10}")

    for label, completion in scenarios:
        planned    = base_load * next_scale
        actual     = planned * completion
        next_scale = controller.log_week(planned, actual)
        if next_scale < 0.99:
            direction = "EASE"
        elif next_scale > 1.01:
            direction = "PROGRESS"
        else:
            direction = "HOLD"
        print(f"  {label:<8}  {planned:>13.1f}  {actual:>12.1f}  "
              f"{completion*100:>10.0f}%  {next_scale:>11.2f}  {direction:>10}")

    print()
    print(SEP)
    print("  Demo complete — all three components functional.")
    print(SEP)


if __name__ == "__main__":
    run_demo()
