"""Tests for divisional chart calculations."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calculations.divisional import (
    compute_divisional_chart, compute_all_divisional_charts,
    _d1_sign, _d2_sign, _d9_sign,
)
from calculations.ephemeris import datetime_to_jd, compute_all_planets, compute_houses


def test_d1_same_as_rashi():
    """D1 sign should match the rashi from longitude."""
    assert _d1_sign(45.0) == 2    # 45° → Taurus
    assert _d1_sign(0.0) == 1     # 0° → Aries
    assert _d1_sign(359.0) == 12  # 359° → Pisces


def test_d2_hora():
    """D2 (Hora) basic checks."""
    # Aries (odd sign, rashi=1): 0–15° → Leo(5), 15–30° → Cancer(4)
    assert _d2_sign(10.0) == 5   # Aries, first half → Leo
    assert _d2_sign(20.0) == 4   # Aries, second half → Cancer

    # Taurus (even sign, rashi=2): 0–15° → Cancer(4), 15–30° → Leo(5)
    assert _d2_sign(40.0) == 4   # Taurus, first half → Cancer
    assert _d2_sign(55.0) == 5   # Taurus, second half → Leo


def test_d9_navamsa():
    """D9 (Navamsa) basic checks."""
    # 0° Aries (fire sign, start=Aries): part 0 → Aries (1)
    assert _d9_sign(0.0) == 1

    # ~3.5° Aries: part 1 → Taurus (2)
    assert _d9_sign(3.5) == 2


def test_all_divisional_charts():
    """All 9 divisional charts should be computed."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, ascmc = compute_houses(jd, 28.6139, 77.2090)

    charts = compute_all_divisional_charts(positions, ascmc[0])
    assert len(charts) == 9

    chart_types = [c["chart_type"] for c in charts]
    for ct in ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D30", "D60"]:
        assert ct in chart_types


def test_divisional_chart_structure():
    """Each divisional chart should have lagna and 9 grahas."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, ascmc = compute_houses(jd, 28.6139, 77.2090)

    chart = compute_divisional_chart(positions, ascmc[0], "D9")
    assert "lagna" in chart
    assert "grahas" in chart
    assert len(chart["grahas"]) == 9
    assert 1 <= chart["lagna"]["rashi"] <= 12
