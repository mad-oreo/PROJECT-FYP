"""L1 and L2 at 20, 63, 64 and 80 km/week."""
import pytest

from pacu.component2 import config
from pacu.component2.long_run import l1_cap_km, l2_cap_km, long_run_km

EASY = 360.0  # 6:00/km -> 150 min = 25 km


@pytest.mark.parametrize("week_km,l1", [(20, 6.0), (63, 18.9), (64, 16.0), (80, 20.0)])
def test_l1(week_km, l1):
    assert l1_cap_km(week_km, EASY, config) == pytest.approx(l1)


def test_l1_high_branch_time_cap():
    # 8:00/km easy: 150 min = 18.75 km < 25% of 80 km = 20
    assert l1_cap_km(80, 480, config) == pytest.approx(18.75)


def test_l2():
    assert l2_cap_km("5K", EASY, config) == 12
    assert l2_cap_km("10K", EASY, config) == 16
    assert l2_cap_km("HM", EASY, config) == 20
    assert l2_cap_km("M", EASY, config) == pytest.approx(25.0)  # 150 min < 32 km
    assert l2_cap_km("M", 270, config) == pytest.approx(32.0)  # 4:30/km: 150 min = 33.3 km


@pytest.mark.parametrize("week_km,dist,km,rule", [
    (20, "M", 6.0, "L1"), (63, "M", 18.9, "L1"), (64, "M", 16.0, "L1"), (80, "M", 20.0, "L1"),
    (20, "5K", 6.0, "L1"), (63, "5K", 12.0, "L2"), (64, "10K", 16.0, "L1"), (80, "HM", 20.0, "L1"),
    (80, "5K", 12.0, "L2"),
])
def test_long_run_is_min_of_l1_l2(week_km, dist, km, rule):
    got_km, got_rule = long_run_km(week_km, dist, EASY, config)
    assert got_km == pytest.approx(km)
    assert got_rule == rule
