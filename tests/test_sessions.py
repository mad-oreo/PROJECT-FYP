"""S1-S7 unit tests, including the brief's S4/S7 worked example at 30 km/week."""
from datetime import date, timedelta

import pytest

from pacu.component2 import config
from pacu.component2.models import MainSet, Session, WeekSpec
from pacu.component2.sessions import (
    build_week, halve_rep, layout_for, s2_violations, s4_cap_km, size_main_set,
)

from helpers import make_ctx, make_inputs, riegel_times


def _ms(zone, pace, unit, length, budget=99.0, week_km=30.0, target=None, jog=120.0):
    return MainSet(workout="T", label="T", zone=zone, pace_s_per_km=pace, unit=unit, nominal_len=length,
                   jog_s=jog, budget_km=budget, week_km_ref=week_km, target_km=target)


# --- S4 / S7 worked example at 30 km/week ---------------------------------

def test_s4_caps_at_30km():
    assert s4_cap_km("Z4", 30, 330, config) == pytest.approx(3.0)
    assert s4_cap_km("Z5_INTERVAL", 30, 330, config) == pytest.approx(2.4)
    assert s4_cap_km("Z5_SHORT", 30, 330, config) == pytest.approx(1.5)
    assert s4_cap_km("Z3", 30, 360, config) == pytest.approx(6.0)


def test_z4_cap_3km_gives_3x1km():
    ms = _ms("Z4", 330, "m", 1000)
    assert size_main_set(ms, config)
    assert (ms.reps, ms.rep_len) == (3, 1000)


def test_z5_interval_cap_gives_6x400m_for_slow_runner():
    ms = _ms("Z5", 340, "m", 400)  # 400 m = 136 s > 2 min -> interval class
    assert size_main_set(ms, config)
    assert ms.s4_class == "Z5_INTERVAL"
    assert (ms.reps, ms.rep_len) == (6, 400)


def test_z5_short_class_for_fast_runner():
    ms = _ms("Z5", 240, "m", 400)  # 400 m = 96 s -> short reps, cap 5% = 1.5 km
    assert size_main_set(ms, config)
    assert ms.s4_class == "Z5_SHORT" and ms.reps == 3


def test_z3_continuous_cap_6km():
    ms = _ms("Z3", 360, "cont", 0)
    assert size_main_set(ms, config)
    assert ms.allowance_km == pytest.approx(6.0) and ms.reps == 1


def test_z3_110_min_cap():
    ms = _ms("Z3", 400, "cont", 0, week_km=300)  # 20% = 60 km, 29 km cap, 110 min = 16.5 km
    size_main_set(ms, config)
    assert ms.allowance_km == pytest.approx(16.5)


def test_p5_budget_limits_allowance():
    ms = _ms("Z4", 330, "m", 1000, budget=2.5)
    size_main_set(ms, config)
    assert ms.reps == 2


# --- S7 halving and A-21 / A-25 ---------------------------------------------

def test_halving_rounds_down_and_floors():
    assert halve_rep(1000, "m", config) == 500
    assert halve_rep(500, "m", config) == 200   # 250 -> 200
    assert halve_rep(200, "m", config) == 200   # floor
    assert halve_rep(300, "s", config) == 150
    assert halve_rep(150, "s", config) == 60    # 75 -> 60 (round down to 30 s, floor 1 min)
    assert halve_rep(480, "s", config) == 240


def test_race_week_target_with_small_cap_halves_reps():
    # P01-like race week: 6.4 km, target 2 x 1 km, Z4 cap 0.64 km -> 3 x 200 m (A-21)
    ms = _ms("Z4", 430, "m", 1000, week_km=6.4, target=2.0, budget=1.28)
    assert size_main_set(ms, config)
    assert (ms.reps, ms.rep_len, ms.halvings) == (3, 200, 2)


def test_time_reps_halve_to_2_30():
    # Long-track race week: 4 x 5 min target, cap 1.27 km at 6:03/km
    ms = _ms("Z4", 363, "s", 300, week_km=12.7, target=4 * 300 / 363, budget=2.54)
    assert size_main_set(ms, config)
    assert ms.rep_len == 150 and ms.reps == 3


def test_too_small_returns_false():
    ms = _ms("Z4", 330, "m", 1000, week_km=3.0)  # cap 0.3 km < 2 x 200 m
    assert not size_main_set(ms, config)
    cont = _ms("Z3", 360, "cont", 0, week_km=5.0)  # 1 km = 6 min < 10 min (A-25)
    assert not size_main_set(cont, config)


def test_scale_reduces_allowance():
    ms = _ms("Z4", 330, "m", 1000)
    ms.scale = 0.9  # A-48: G2 scales the allowance, 2.7 km -> 2 reps
    size_main_set(ms, config)
    assert ms.reps == 2


# --- S2 ----------------------------------------------------------------------

def _layout_sessions(capacity, lrw, weeks=3, start=date(2026, 12, 7)):
    out = []
    for w in range(weeks):
        s0 = start + timedelta(days=7 * w)
        spec = WeekSpec(label=str(w), plan_index=w + 1, start_date=s0, end_date=s0 + timedelta(days=6),
                        daniels_phase="II", pacu_phase="build", week_type="normal", level_km=30,
                        long_run_weekday=lrw)
        for d, slot in layout_for(spec, capacity, config).items():
            if slot:
                out.append(Session(date=d, slot=slot))
    return out


@pytest.mark.parametrize("capacity", config.CAPACITIES)
@pytest.mark.parametrize("lrw", range(7))
def test_s2_layout_every_capacity_and_weekday(capacity, lrw):
    sessions = _layout_sessions(capacity, lrw)
    assert s2_violations(sessions, config) == []
    hard = sum(1 for s in sessions if s.slot == "HARD")
    assert hard == 3 * config.HARD_SESSIONS_PER_WEEK[capacity]


def test_s2_detects_violations():
    d = date(2027, 1, 4)
    bad = [Session(date=d, slot="LONG"), Session(date=d + timedelta(1), slot="HARD"),
           Session(date=d + timedelta(3), slot="HARD")]
    assert len(s2_violations(bad, config)) == 2


# --- build_week ----------------------------------------------------------

def _spec(label, idx, start, phase_d, phase_p, wtype, level, lrw=6):
    return WeekSpec(label=label, plan_index=idx, start_date=start, end_date=start + timedelta(days=6),
                    daniels_phase=phase_d, pacu_phase=phase_p, week_type=wtype, level_km=level,
                    long_run_weekday=lrw)


def test_base_week_is_all_easy_with_strides():
    ctx = make_ctx(make_inputs())  # 10K Standard, 30 km
    spec = _spec("1", 1, date(2026, 12, 7), "I", "base", "normal", 30.0)
    w = build_week(spec, ctx, [], [spec])
    assert [s.slot for s in w.sessions] == ["EASY", "EASY", "EASY", "LONG"]
    assert sum(1 for s in w.sessions if s.strides == 6) == 2  # the two HARD slots
    assert w.km == pytest.approx(30.0)
    assert w.easy_share == pytest.approx(1.0)
    assert next(s for s in w.sessions if s.slot == "LONG").km == pytest.approx(9.0)


def test_build_week_standard_short_track():
    ctx = make_ctx(make_inputs())
    spec = _spec("5", 5, date(2027, 1, 4), "II", "build", "normal", 36.4)
    w = build_week(spec, ctx, [], [spec])
    hards = sorted(w.hard_sessions, key=lambda s: s.date)
    assert [h.main_set.workout for h in hards] == ["Z4_1K_REPS", "Z3_TEMPO"]
    assert hards[0].main_set.reps == 3  # min(10% of 36.4, 20%/2) = 3.64 km
    assert w.km == pytest.approx(36.4)
    assert w.easy_share >= 0.8 - 1e-9
    assert all(s.rule_trace for s in w.sessions) and w.rule_trace


def test_race_week_standard_default_long_run_day():
    inp = make_inputs()  # race Sunday 2027-03-28, long run defaults to Sunday
    ctx = make_ctx(inp)
    start = inp.race_date - timedelta(days=6)
    spec = _spec("16", 16, start, "IV", "taper", "race", 20.0, lrw=6)
    w = build_week(spec, ctx, [], [spec])
    slots = {s.date.weekday(): s.slot for s in w.sessions}
    assert slots == {1: "HARD", 3: "EASY", 4: "EASY", 6: "RACE"}  # Tue hard = 5 days out
    race = next(s for s in w.sessions if s.slot == "RACE")
    assert w.km == pytest.approx(20.0)  # race excluded (A-4)
    assert race.load is None


def test_race_week_long_run_day_differs():
    inp = make_inputs(long_run_weekday=5)  # Saturday long run, Sunday race (P13)
    ctx = make_ctx(inp)
    start = inp.race_date - timedelta(days=6)
    spec = _spec("16", 16, start, "IV", "taper", "race", 20.0, lrw=5)
    w = build_week(spec, ctx, [], [spec])
    assert not any(s.slot == "LONG" for s in w.sessions)
    hard = w.hard_sessions
    assert len(hard) == 1 and (inp.race_date - hard[0].date).days in (4, 5, 6)


def test_injury_pauses_hard_sessions():
    ctx = make_ctx(make_inputs())
    spec = _spec("5", 5, date(2027, 1, 4), "II", "build", "normal", 36.4)
    spec.hard_paused = True
    w = build_week(spec, ctx, [], [spec])
    assert w.hard_sessions == []
    assert all(s.strides == 0 for s in w.sessions)  # strides only in base/hold
    assert any(s.has_note("HARD_PAUSED_INJURY") for s in w.sessions)


def test_conservative_long_run_not_longest_note():
    ctx = make_ctx(make_inputs(target_distance="5K", current_weekly_km=8, recovery_answers=(3, 3, 3),
                               predicted_times_s=riegel_times(2160), easy_pace_s_per_km=510,
                               race_date=date(2027, 2, 7)))
    spec = _spec("1", 1, date(2026, 12, 7), "I", "base", "normal", 8.0)
    w = build_week(spec, ctx, [], [spec])
    assert w.has_note("LONG_RUN_NOT_LONGEST")
    assert any(s.has_note("EASY_RUN_UNDER_30_MIN") for s in w.sessions)
