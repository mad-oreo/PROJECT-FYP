"""P3 (Fig. 10.2), A-1, T1, P4."""
import pytest

from components.component2 import config
from components.component2.phases import phase_lengths, plan_phases, taper_length


@pytest.mark.parametrize("n,lengths", [
    (6, (3, 0, 0, 3)), (9, (3, 3, 0, 3)), (12, (3, 3, 3, 3)), (16, (4, 3, 6, 3)),
    (18, (4, 4, 6, 4)), (20, (4, 6, 6, 4)), (24, (6, 6, 6, 6)),
])
def test_fig_10_2_phase_lengths(n, lengths):
    pl = phase_lengths(n, config)
    assert (pl["I"], pl["II"], pl["III"], pl["IV"]) == lengths
    assert sum(pl.values()) == n


def test_every_n_sums_to_n():
    for n in range(2, 25):
        assert sum(phase_lengths(n, config).values()) == n


def test_marathon_18_weeks_mapping():
    ph = plan_phases(18, "M", config)
    assert [p.pacu_phase for p in ph[:4]] == ["base"] * 4
    assert [p.pacu_phase for p in ph[4:8]] == ["build"] * 4
    assert [p.pacu_phase for p in ph[8:15]] == ["peak"] * 7  # III (6) + first IV week
    assert [p.pacu_phase for p in ph[15:]] == ["taper"] * 3
    assert [p.week_type for p in ph[15:]] == ["taper", "taper", "race"]
    # P4: weeks 4, 8, 12 are recovery; week 16 is taper so not recovery
    assert [p.plan_index for p in ph if p.week_type == "recovery"] == [4, 8, 12]


def test_short_track_taper_is_race_week_only():
    ph = plan_phases(9, "5K", config)
    assert [p.week_type for p in ph if p.pacu_phase == "taper"] == ["race"]
    assert ph[7].week_type == "recovery"  # week 8 is a P4 recovery week


def test_taper_length_a28():
    assert taper_length("M", 18, config) == 3
    assert taper_length("M", 3, config) == 2  # at least 1 non-taper week
    assert taper_length("HM", 2, config) == 1
    ph = plan_phases(3, "5K", config)
    # A-28: race week overrides base when N is tiny
    assert ph[-1].pacu_phase == "taper" and ph[-1].daniels_phase == "I"
