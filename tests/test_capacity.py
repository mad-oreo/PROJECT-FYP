"""C rules: band boundaries and priority resolution."""
import pytest

from pacu.component2 import config
from pacu.component2.capacity import (
    decide_capacity, fired_rules, mileage_band, recovery_band, v2_step_km,
)


@pytest.mark.parametrize("km,band", [(19, "Low"), (19.99, "Low"), (20, "Moderate"), (40, "Moderate"),
                                     (40.01, "High"), (41, "High")])
def test_mileage_band_boundaries(km, band):
    assert mileage_band(km, config) == band


@pytest.mark.parametrize("score,band", [(3, "Low"), (7, "Low"), (8, "Moderate"), (11, "Moderate"),
                                        (12, "High"), (15, "High")])
def test_recovery_band_boundaries(score, band):
    assert recovery_band(score, config) == band


@pytest.mark.parametrize("km,answers,cap,rule", [
    (19, (4, 4, 4), "Conservative", "C2"),   # mileage low
    (20, (4, 4, 4), "Standard", "C4"),       # moderate mileage, high recovery
    (40, (5, 5, 5), "Standard", "C4"),       # 40 is still moderate
    (41, (4, 4, 4), "Progressive", "C3"),    # high + high
    (41, (4, 4, 3), "Standard", "C4"),       # high mileage, score 11 = moderate
    (41, (3, 2, 2), "Conservative", "C1"),   # score 7 = low recovery
    (30, (3, 3, 2), "Standard", "C4"),       # score 8 = moderate
])
def test_capacity_boundaries(km, answers, cap, rule):
    assert decide_capacity(km, answers, config)[:2] == (cap, rule)


def test_priority_c1_beats_c2():
    # Both C1 (recovery low) and C2 (mileage low) fire; C1 has priority 1.
    assert [r for r, _ in fired_rules(10, 6, config)] == ["C1", "C2"]
    assert decide_capacity(10, (2, 2, 2), config)[:2] == ("Conservative", "C1")


def test_priority_c1_beats_c3_path():
    # High mileage with low recovery must not become Progressive.
    assert decide_capacity(60, (1, 2, 3), config)[:2] == ("Conservative", "C1")


def test_recovery_score_is_sum():
    assert decide_capacity(30, (5, 4, 4), config)[2] == 13


def test_v2_steps():
    assert [v2_step_km(c, config) for c in config.CAPACITIES] == pytest.approx([4.8, 6.4, 8.0])
