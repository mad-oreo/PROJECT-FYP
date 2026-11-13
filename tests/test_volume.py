"""V1-V4 and P4 levels."""
import pytest

from pacu.component2 import config
from pacu.component2.phases import plan_phases
from pacu.component2.volume import below_entry_minimum, entry_suggestions, weekly_levels


def test_v2_sequence_10km_conservative():
    ph = plan_phases(20, "M", config)
    levels, notes = weekly_levels(ph, 10.0, "Conservative", "M", config)
    assert levels[:12] == pytest.approx([10, 10, 10, 8, 14.8, 14.8, 14.8, 11.84, 19.6, 19.6, 19.6, 15.68])
    assert notes == []


def test_v3_peak_cap_holds():
    ph = plan_phases(16, "10K", config)
    levels, _ = weekly_levels(ph, 30.0, "Standard", "10K", config)
    assert levels[:12] == pytest.approx([30, 30, 30, 24, 36.4, 36.4, 36.4, 29.12, 40, 40, 40, 32])
    assert levels[12:15] == pytest.approx([40, 40, 40])
    assert levels[15] is None  # race week, filled by T2
    assert max(v for v in levels if v is not None) <= 40


def test_above_peak_target_holds_current():
    ph = plan_phases(12, "5K", config)
    levels, notes = weekly_levels(ph, 50.0, "Progressive", "5K", config)
    assert [m.code for m in notes] == ["ABOVE_PEAK_TARGET"]
    assert levels[:11] == pytest.approx([50, 50, 50, 40, 50, 50, 50, 40, 50, 50, 50])


def test_entry_minimum_and_suggestions():
    assert below_entry_minimum("M", 15, config)
    assert not below_entry_minimum("HM", 15, config)  # 15 is not below 15
    codes = [m.code for m in entry_suggestions("M", 15, config)]
    assert codes == ["TRY_5K", "TRY_10K", "TRY_HM", "CHOOSE_LATER_RACE"]
    codes = [m.code for m in entry_suggestions("HM", 7, config)]
    assert codes == ["TRY_5K", "CHOOSE_LATER_RACE"]
