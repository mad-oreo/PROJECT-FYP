"""T2 taper levels."""
import pytest

from components.component2 import config
from components.component2.phases import plan_phases
from components.component2.taper import taper_levels
from components.component2.volume import weekly_levels


def test_marathon_taper_sequence():
    # P08-like: M, Standard, 35 km, N = 18. Week 15 (54.2) is the A-8 reference.
    ph = plan_phases(18, "M", config)
    levels = taper_levels(weekly_levels(ph, 35.0, "Standard", "M", config)[0], ph, config)
    ref = levels[14]
    assert ref == pytest.approx(54.2)
    assert levels[15:] == pytest.approx([0.75 * ref, 0.75 ** 2 * ref, 0.5 * 0.75 ** 2 * ref])


def test_taper_reference_skips_recovery_week():
    # 5K N=9: week 8 is a recovery week, so race week = 50% of week 7 (A-8).
    ph = plan_phases(9, "5K", config)
    levels = taper_levels(weekly_levels(ph, 8.0, "Conservative", "5K", config)[0], ph, config)
    assert levels[7] == pytest.approx(0.8 * 12.8)
    assert levels[8] == pytest.approx(0.5 * 12.8)


def test_half_marathon_taper():
    ph = plan_phases(14, "HM", config)
    levels = taper_levels(weekly_levels(ph, 21.0, "Standard", "HM", config)[0], ph, config)
    ref = levels[10]  # week 12 is a recovery week, so week 11 is the A-8 reference
    assert ref == pytest.approx(33.8) and ph[11].week_type == "recovery"
    assert ph[12].week_type == "taper" and ph[13].week_type == "race"
    assert levels[12:] == pytest.approx([0.75 * ref, 0.375 * ref])
