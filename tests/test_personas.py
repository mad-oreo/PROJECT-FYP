"""Persona conformance tests (brief section 9), under both load methods."""
from functools import lru_cache

import pytest

from components.component2 import config, generate_plan
from components.component2.long_run import l1_cap_km, l2_cap_km
from components.component2.serialize import plan_to_json
from components.component2.sessions import s2_violations, s4_cap_km
from personas.loader import all_personas

PERSONAS = all_personas()
IDS = [meta["id"] for meta, _ in PERSONAS]
METHODS = list(config.LOAD_METHODS)
TOL = 1e-9


@lru_cache(maxsize=None)
def plan_for(pid: str, method: str):
    _, inputs = next(p for p in PERSONAS if p[0]["id"] == pid)
    return generate_plan(inputs, config.with_overrides(LOAD_METHOD=method))


OK_IDS = [pid for pid in IDS if plan_for(pid, "session").status == "OK"]


# --- expectations ------------------------------------------------------------

@pytest.mark.parametrize("pid", IDS)
def test_persona_expectations(pid):
    meta = next(m for m, _ in PERSONAS if m["id"] == pid)
    exp, p = meta["expect"], plan_for(pid, "session")
    assert p.status == exp["status"]
    assert (p.capacity, p.c_rule) == (exp["capacity"], exp["c_rule"])
    if p.status == "OK":
        assert (p.N, p.hold_weeks) == (exp["N"], exp["hold_weeks"])
    assert [m.code for m in p.warnings] == exp["warnings"]
    assert [m.code for m in p.notes] == exp["notes"]
    assert [m.code for m in p.advisories] == exp["advisories"]
    if "suggestions" in exp:
        assert [m.code for m in p.suggestions] == exp["suggestions"]
    if exp.get("no_hard_sessions"):
        assert all(s.slot != "HARD" for w in p.weeks for s in w.sessions)
    if exp.get("race_week_long_run") is False:
        assert not any(s.slot == "LONG" for s in p.weeks[-1].sessions)


@pytest.mark.parametrize("pid", OK_IDS)
def test_deterministic(pid):
    _, inputs = next(p for p in PERSONAS if p[0]["id"] == pid)
    assert plan_to_json(generate_plan(inputs)) == plan_to_json(generate_plan(inputs))


# --- conformance, every week ---------------------------------------------------

@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("pid", OK_IDS)
def test_conformance(pid, method):
    p = plan_for(pid, method)
    cfg, ctx = p.context.cfg, p.context
    easy = ctx.paces.easy
    all_sessions = [s for w in p.weeks for s in w.sessions]

    assert s2_violations(all_sessions, cfg) == []  # S2 incl. week boundaries
    for w in p.weeks:
        assert w.acwr <= cfg.ACWR_CAP + TOL, w.label                      # G1/G2
        assert w.easy_share >= cfg.MIN_EASY_SHARE - TOL, w.label          # P6
        assert w.rule_trace, w.label
        for s in w.sessions:
            assert s.rule_trace, (w.label, s.date)
            if s.slot == "LONG":                                          # L1, L2
                assert s.km <= l1_cap_km(w.km, easy, cfg) + TOL, w.label
                assert s.km <= l2_cap_km(ctx.distance, easy, cfg) + TOL, w.label
            if s.slot == "HARD":                                          # S4 on actual km
                ms = s.main_set
                assert ms.main_km <= s4_cap_km(ms.s4_class, w.km, ms.pace_s_per_km, cfg) + TOL, w.label
        if w.week_type != "race":                                         # runs per week
            assert len(w.runs) == cfg.RUNS_PER_WEEK[ctx.capacity], w.label
        if w.pacu_phase in ("base", "hold") or w.week_type in ("recovery", "hold"):
            assert w.hard_sessions == [], w.label                         # A-2, P4, A-18
        if not w.governor["fired"]:
            assert w.km == pytest.approx(w.level_km), w.label             # levels respected
        if w.week_type == "race":                                         # A-7
            race_day = p.inputs.race_date
            assert all((race_day - s.date).days > cfg.RACE_WEEK_NO_HARD_WITHIN_DAYS for s in w.hard_sessions)
            assert len(w.hard_sessions) <= 1


@pytest.mark.parametrize("pid", OK_IDS)
def test_taper_levels_follow_t2(pid):
    p = plan_for(pid, "session")
    cfg = p.context.cfg
    plan_weeks = [w for w in p.weeks if w.spec.plan_index is not None]
    prev = [w for w in plan_weeks if w.week_type == "normal"][-1].level_km  # A-8 reference
    for w in plan_weeks:
        if w.week_type == "taper":
            assert w.level_km == pytest.approx(cfg.TAPER_WEEK_FRACTION * prev)
        elif w.week_type == "race":
            assert w.level_km == pytest.approx(cfg.RACE_WEEK_FRACTION * prev)
        else:
            continue
        prev = w.level_km
    assert plan_weeks[-1].week_type == "race"
