"""Section 7: the functions Component 3 will call."""
from datetime import date

import pytest

from pacu.component2 import (
    change_long_run_day, clear_injury_flag, generate_plan, govern_week, make_recovery_week,
)
from pacu.component2.engine import load_history
from pacu.component2.sessions import s2_violations

from helpers import make_inputs, riegel_times

CASES = {  # one per capacity
    "Conservative": dict(target_distance="HM", current_weekly_km=19, recovery_answers=(4, 4, 4),
                         easy_pace_s_per_km=420, predicted_times_s=riegel_times(1740), race_date=date(2027, 3, 14)),
    "Standard": dict(),
    "Progressive": dict(target_distance="HM", current_weekly_km=45, recovery_answers=(5, 4, 4),
                        easy_pace_s_per_km=350, predicted_times_s=riegel_times(1380), race_date=date(2027, 3, 14)),
}


def _all_sessions(plan):
    return [s for w in plan.weeks for s in w.sessions]


def test_govern_week_is_exported_and_idempotent_on_plan_weeks():
    p = generate_plan(make_inputs())
    w = p.weeks[5]
    acwr = w.acwr
    govern_week(w, load_history(p, 5), p.context.cfg)
    assert w.acwr == pytest.approx(acwr)


def test_make_recovery_week():
    p = generate_plan(make_inputs())
    q = make_recovery_week(p, "6")
    w = q.week("6")
    assert w.week_type == "recovery" and w.hard_sessions == []
    assert w.level_km == pytest.approx(0.8 * q.week("5").level_km)
    assert all(x.acwr <= 1.5 + 1e-9 for x in q.weeks)
    assert [x.level_km for x in q.weeks[6:]] == [x.level_km for x in p.weeks[6:]]  # later levels kept (G4)
    assert p.week("6").week_type == "normal"  # original plan untouched
    assert "RECOVERY_WEEK_INSERTED" in [n.code for n in q.notes]


def test_make_recovery_week_rejects_taper():
    p = generate_plan(make_inputs())
    with pytest.raises(ValueError):
        make_recovery_week(p, str(p.N))


@pytest.mark.parametrize("capacity", list(CASES))
@pytest.mark.parametrize("new_day", range(7))
def test_change_long_run_day(capacity, new_day):
    p = generate_plan(make_inputs(**CASES[capacity]))
    assert p.capacity == capacity
    q = change_long_run_day(p, new_day, "6")
    i = q.week_index("6")
    for w in q.weeks[i:]:
        for s in w.sessions:
            if s.slot == "LONG":
                assert s.date.weekday() == new_day
        assert w.level_km == p.weeks[q.week_index(w.label)].level_km  # volumes kept
        assert w.acwr <= 1.5 + 1e-9
    violations = s2_violations(_all_sessions(q), q.context.cfg)
    if violations:  # only the documented A-26 case may remain, and it must be flagged
        assert q.week("6").has_note("S2_TRANSITION_UNRESOLVED")
        assert len(violations) == 1


def test_clear_injury_flag():
    p = generate_plan(make_inputs(target_distance="5K", current_weekly_km=15, recovery_answers=(3, 3, 3),
                                  injury_flag=True, race_date=date(2027, 2, 14),
                                  predicted_times_s=riegel_times(1920), easy_pace_s_per_km=450))
    assert all(s.slot != "HARD" for s in _all_sessions(p))
    q = clear_injury_flag(p, "5")
    i = q.week_index("5")
    assert all(s.slot != "HARD" for w in q.weeks[:i] for s in w.sessions)
    assert any(s.slot == "HARD" for w in q.weeks[i:] for s in w.sessions)
    assert q.advisories == [] and "INJURY_CLEARED" in [n.code for n in q.notes]
    assert all(w.acwr <= 1.5 + 1e-9 for w in q.weeks)
    assert s2_violations(_all_sessions(q), q.context.cfg) == []
