"""G1-G3, including the brief's G2 worked check."""
from datetime import date, timedelta

import pytest

from pacu.component2 import config
from pacu.component2.long_run import l1_cap_km, l2_cap_km
from pacu.component2.governor import chronic_load, govern_week
from pacu.component2.models import WeekSpec
from pacu.component2.sessions import build_week, s4_cap_km

from helpers import make_ctx, make_inputs

EASY = 360.0  # 6:00/km: all-easy load = km x 6 x 3.5 = 21 x km


def _spec(level, phase_d="I", phase_p="base", wtype="normal", idx=5):
    start = date(2027, 1, 4)
    return WeekSpec(label=str(idx), plan_index=idx, start_date=start, end_date=start + timedelta(days=6),
                    daniels_phase=phase_d, pacu_phase=phase_p, week_type=wtype, level_km=level,
                    long_run_weekday=6)


def test_g2_worked_check():
    ctx = make_ctx(make_inputs(easy_pace_s_per_km=EASY, current_weekly_km=10), capacity="Conservative")
    spec = _spec(14.8)
    week = build_week(spec, ctx, [], [spec])
    prev = [21 * km for km in (10, 10, 10, 8)]
    assert week.load / chronic_load(prev, config) == pytest.approx(14.8 / 9.5)  # ~1.558
    govern_week(week, prev, config)
    assert week.governor["fired"]
    assert week.km == pytest.approx(14.25)
    assert week.acwr == pytest.approx(1.5)
    assert week.level_km == 14.8  # G4: the planned level is not changed
    assert "G2" in week.rule_trace and week.has_note("G2")


def test_no_cut_when_within_cap():
    ctx = make_ctx(make_inputs(easy_pace_s_per_km=EASY))
    spec = _spec(14.0)
    week = govern_week(build_week(spec, ctx, [], [spec]), [21 * 10] * 4, config)
    assert not week.governor["fired"] and week.km == pytest.approx(14.0)
    assert week.acwr == pytest.approx(1.4)


def test_hard_week_is_governed_and_caps_hold():
    ctx = make_ctx(make_inputs())  # 10K Standard, easy 6:40
    spec = _spec(36.4, "II", "build", idx=5)
    week = build_week(spec, ctx, [], [spec])
    base = 30 * (400 / 60) * 3.5
    prev = [base, base, base, 0.8 * base]
    govern_week(week, prev, config)
    assert week.governor["fired"] and week.acwr <= 1.5 + 1e-9
    assert week.km < 36.4
    for s in week.hard_sessions:
        ms = s.main_set
        assert ms.main_km <= s4_cap_km(ms.s4_class, week.km, ms.pace_s_per_km, config) + 1e-9
    long = next(s for s in week.sessions if s.slot == "LONG")
    assert long.km <= min(l1_cap_km(week.km, 400, config), l2_cap_km("10K", 400, config)) + 1e-9
    assert week.easy_share >= 0.70


def test_last_resort_converts_hard_sessions():
    cfg = config.with_overrides(G2_MAX_ITERATIONS=1)
    ctx = make_ctx(make_inputs(), cfg=cfg)
    spec = _spec(36.4, "II", "build", idx=5)
    week = build_week(spec, ctx, [], [spec])
    govern_week(week, [300.0] * 4, cfg)  # chronic far below this week's load
    assert week.acwr <= 1.5 + 1e-9
    assert any(s.has_note("G2_HARD_TO_EASY") or s.has_note("HARD_SESSION_TOO_SMALL") for s in week.sessions)


def test_chronic_load_errors():
    with pytest.raises(ValueError):
        chronic_load([0, 0, 0, 0], config)
    with pytest.raises(ValueError):
        chronic_load([100, 100], config)
