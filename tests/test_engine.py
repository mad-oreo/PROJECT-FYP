"""Section 5 pipeline: validation, V4 entry, hold weeks, injury, race."""
from datetime import date, timedelta

import pytest

from components.component2 import generate_plan

from helpers import make_inputs, riegel_times


@pytest.mark.parametrize("kw", [
    dict(recovery_answers=(0, 3, 3)), dict(recovery_answers=(3, 3, 6)), dict(recovery_answers=(3, 3)),
    dict(race_date=date(2026, 12, 7)), dict(target_distance="50K"), dict(long_run_weekday=7),
    dict(current_weekly_km=-1), dict(predicted_times_s={"5K": 1500}), dict(max_hr=0),
    dict(race_date=date(2026, 12, 15)),  # only 1 whole week (A-28)
])
def test_invalid_inputs_raise(kw):
    with pytest.raises(ValueError):
        generate_plan(make_inputs(**kw))


def test_easy_pace_too_fast_warning():
    p = generate_plan(make_inputs(easy_pace_s_per_km=300))  # faster than 6:15/km marathon pace
    assert "EASY_PACE_TOO_FAST" in [w.code for w in p.warnings]
    assert p.status == "OK"


def test_below_entry_minimum_no_plan():
    p = generate_plan(make_inputs(target_distance="M", current_weekly_km=15, recovery_answers=(4, 4, 4),
                                  race_date=date(2027, 4, 25)))
    assert p.status == "BELOW_ENTRY_MINIMUM" and p.weeks == []
    assert [s.code for s in p.suggestions] == ["TRY_5K", "TRY_10K", "TRY_HM", "CHOOSE_LATER_RACE"]


def test_override_entry_minimum():
    p = generate_plan(make_inputs(target_distance="M", current_weekly_km=15, override_entry_minimum=True,
                                  race_date=date(2027, 4, 25)))
    assert p.status == "OK" and "BELOW_ENTRY_MINIMUM" in [w.code for w in p.warnings]
    p0 = generate_plan(make_inputs(target_distance="5K", current_weekly_km=0, override_entry_minimum=True))
    assert p0.status == "BELOW_ENTRY_MINIMUM"  # A-11: override needs current km > 0


def test_hold_weeks():
    p = generate_plan(make_inputs(target_distance="M", current_weekly_km=50, recovery_answers=(5, 5, 4),
                                  easy_pace_s_per_km=330, predicted_times_s=riegel_times(1290),
                                  race_date=date(2027, 7, 4)))
    assert (p.N, p.hold_weeks) == (24, 6)
    assert [w.label for w in p.weeks[:7]] == ["H1", "H2", "H3", "H4", "H5", "H6", "1"]
    for w in p.weeks[:6]:
        assert w.week_type == "hold" and w.level_km == 50 and w.hard_sessions == []
    for a, b in zip(p.weeks, p.weeks[1:]):
        assert b.start_date - a.end_date == timedelta(days=1)
    assert p.weeks[-1].end_date == date(2027, 7, 4)


def test_injury_flag_pauses_all_hard_sessions():
    p = generate_plan(make_inputs(target_distance="5K", current_weekly_km=15, recovery_answers=(3, 3, 3),
                                  injury_flag=True, race_date=date(2027, 2, 14)))
    assert [a.code for a in p.advisories] == ["INJURY_FLAG"]
    assert "paused" in p.advisories[0].message
    assert all(s.slot != "HARD" for w in p.weeks for s in w.sessions)


def test_default_long_run_day_is_race_weekday():
    p = generate_plan(make_inputs())
    longs = {s.date.weekday() for w in p.weeks for s in w.sessions if s.slot == "LONG"}
    assert longs == {6}  # Sunday, like the race


def test_race_reported_separately():
    p = generate_plan(make_inputs())
    assert p.race["date"] == date(2027, 3, 28) and p.race["km"] == 10.0
    last = p.weeks[-1]
    race = [s for s in last.sessions if s.slot == "RACE"]
    assert len(race) == 1 and race[0].date == p.race["date"]
    assert last.km == pytest.approx(sum(s.km for s in last.sessions if s.slot != "RACE"))


def test_summary_fields():
    s = generate_plan(make_inputs()).summary
    for key in ("peak_km_reached", "reached_peak_target", "g2_fire_count", "max_acwr", "min_easy_share",
                "plan_easy_share", "max_long_run_km", "easy_run_under_30_min", "hard_session_too_small",
                "long_run_not_longest_weeks", "avg_build_increase_pct"):
        assert key in s
