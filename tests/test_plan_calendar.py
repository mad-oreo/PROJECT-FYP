"""P1, P2, P2b."""
from datetime import date, timedelta

import pytest

from components.component2 import config
from components.component2.plan_calendar import length_messages, minimum_weeks, plan_calendar

START = date(2026, 12, 7)  # Monday


@pytest.mark.parametrize("race,n,hold", [
    (date(2027, 2, 7), 9, 0), (date(2027, 2, 28), 12, 0), (date(2027, 3, 28), 16, 0),
    (date(2027, 3, 14), 14, 0), (date(2027, 4, 25), 20, 0), (date(2027, 4, 11), 18, 0),
    (date(2027, 7, 4), 24, 6), (date(2027, 1, 31), 8, 0), (date(2027, 2, 14), 10, 0),
])
def test_persona_week_counts(race, n, hold):
    cal = plan_calendar(START, race, config)
    assert (cal.n_weeks, cal.hold_weeks) == (n, hold)


def test_weeks_end_on_race_day_and_are_contiguous():
    race = date(2027, 7, 4)
    cal = plan_calendar(START, race, config)
    assert cal.week_dates[-1][1] == race
    allw = cal.hold_dates + cal.week_dates
    for (s, e) in allw:
        assert (e - s).days == 6
    for (_, e1), (s2, _) in zip(allw, allw[1:]):
        assert s2 - e1 == timedelta(days=1)
    assert allw[0][0] >= START


def test_leftover_days_unscheduled():
    # Start Wednesday, race Sunday 9 weeks + 4 days later: 4 leftover days.
    start, race = date(2026, 12, 2), date(2027, 2, 7)
    cal = plan_calendar(start, race, config)
    assert cal.leftover_days == ((race - start).days + 1) % 7
    assert cal.week_dates[0][0] == start + timedelta(days=cal.leftover_days)


def test_too_short_raises():
    with pytest.raises(ValueError):
        plan_calendar(START, START + timedelta(days=12), config)  # 13 days = 1 whole week
    assert plan_calendar(START, START + timedelta(days=13), config).n_weeks == 2


def test_p2_minimums():
    assert minimum_weeks("5K", "Standard", config) == 6
    assert minimum_weeks("HM", "Standard", config) == 9
    assert minimum_weeks("M", "Standard", config) == 12
    assert minimum_weeks("M", "Conservative", config) == 18
    w, _ = length_messages("M", "Standard", 8, config)
    assert [m.code for m in w] == ["PLAN_SHORTER_THAN_MINIMUM"]
    w, _ = length_messages("M", "Conservative", 18, config)
    assert w == []


@pytest.mark.parametrize("n,noted", [(7, True), (8, False), (9, False), (12, False), (13, True)])
def test_p2b_5k_note(n, noted):
    _, notes = length_messages("5K", "Standard", n, config)
    assert (notes != []) == noted
    _, notes = length_messages("10K", "Standard", n, config)
    assert notes == []
