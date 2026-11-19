"""Z rules."""
import pytest

from components.component2 import config
from components.component2.zones import build_paces, hr_range, is_easy, load_rpe

from helpers import make_inputs, riegel_times


def test_paces_follow_z_rules():
    t = riegel_times(1650)  # 27:30 5K
    p = build_paces(make_inputs(predicted_times_s=t, easy_pace_s_per_km=400), config)
    assert p.easy == 400 and p.z1 == 430
    assert p.z4 == pytest.approx(t["10K"] / 10)
    assert p.z5 == pytest.approx(t["5K"] / 5)
    assert p.z3_tempo == pytest.approx((t["M"] / 42.195 + t["HM"] / 21.0975) / 2)
    assert p.race == pytest.approx(t["10K"] / 10)


def test_long_track_race_pace_uses_target_pace():
    t = riegel_times(1560)
    pm = build_paces(make_inputs(target_distance="M", predicted_times_s=t), config)
    ph = build_paces(make_inputs(target_distance="HM", predicted_times_s=t), config)
    assert pm.z3_race == pytest.approx(t["M"] / 42.195)
    assert ph.z3_race == pytest.approx(t["HM"] / 21.0975)


def test_load_rpe_midpoints_and_easy_zones():
    assert [load_rpe(z, config) for z in config.ZONES] == [1.5, 3.5, 5.5, 7.5, 9.5]
    assert is_easy("Z1", config) and is_easy("Z2", config) and not is_easy("Z3", config)


def test_hr_range_only_with_max_hr():
    assert hr_range("Z2", None, config) is None
    assert hr_range("Z2", 200, config) == (146, 160)
    assert hr_range("Z1", 200, config) == (None, 144)
    assert hr_range("Z5", 200, config) == (186, None)
