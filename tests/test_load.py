"""S6 load methods and the G6 baseline."""
from datetime import date

import pytest

from components.component2 import config
from components.component2.load import baseline_load, session_load
from components.component2.models import Segment, Session


def _hard():
    s = Session(date=date(2027, 1, 5), slot="HARD", main_zone="Z4")
    s.segments = [Segment("warmup", 2.0, "Z1", 420), Segment("rep", 3.0, "Z4", 330),
                  Segment("cooldown", 2.0, "Z1", 420)]
    return s


def test_session_method_uses_main_zone_rpe_for_whole_session():
    s = _hard()
    minutes = (2 * 420 + 3 * 330 + 2 * 420) / 60
    assert session_load(s, config) == pytest.approx(minutes * 7.5)


def test_segment_method_uses_each_segment_zone():
    s = _hard()
    cfg = config.with_overrides(LOAD_METHOD="segment")
    expected = (4 * 420 / 60) * 1.5 + (3 * 330 / 60) * 7.5
    assert session_load(s, cfg) == pytest.approx(expected)


def test_race_has_no_load():
    s = Session(date=date(2027, 1, 5), slot="RACE", segments=[Segment("steady", 10, None, 300)])
    assert session_load(s, config) is None


def test_baseline_load():
    # 10 km at 6:00/km x 3.5 = 210
    assert baseline_load(10, 360, config) == pytest.approx(210)
