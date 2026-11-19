"""Sanity checks on config.py (every number lives there)."""
import pytest

from components.component2 import config


def test_v2_step_is_1_6_km_per_run():
    steps = {c: config.V2_KM_PER_RUN * r for c, r in config.RUNS_PER_WEEK.items()}
    assert steps == pytest.approx({"Conservative": 4.8, "Standard": 6.4, "Progressive": 8.0})


def test_daniels_fig_10_2_covers_weeks_1_to_24_once():
    weeks = sorted(w for ws in config.DANIELS_PHASE_WEEKS.values() for w in ws)
    assert weeks == list(range(1, 25))


def test_layout_has_one_slot_per_run():
    for cap, layout in config.LAYOUT.items():
        assert len(layout) == config.RUNS_PER_WEEK[cap]
        assert sum(1 for s in layout.values() if s == "HARD") == config.HARD_SESSIONS_PER_WEEK[cap]


def test_with_overrides():
    cfg = config.with_overrides(LOAD_METHOD="segment")
    assert cfg.LOAD_METHOD == "segment" and cfg.ACWR_CAP == config.ACWR_CAP
    assert config.LOAD_METHOD == "session"  # module itself untouched
    with pytest.raises(AttributeError):
        config.with_overrides(NOT_A_CONSTANT=1)
    with pytest.raises(ValueError):
        config.with_overrides(LOAD_METHOD="bogus")
