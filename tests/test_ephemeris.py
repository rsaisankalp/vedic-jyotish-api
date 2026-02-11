"""Tests for ephemeris calculations."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calculations.ephemeris import (
    datetime_to_jd, local_time_to_ut_hour, compute_all_planets,
    compute_houses, get_ayanamsa,
)


def test_julian_day():
    """Test Julian Day calculation for a known date."""
    # J2000.0 = 2000-01-01 12:00 UT → JD 2451545.0
    jd = datetime_to_jd(2000, 1, 1, 12.0)
    assert abs(jd - 2451545.0) < 0.001


def test_local_to_ut():
    """Test local time to UT conversion."""
    # 14:30:00 IST (UTC+5.5) → 09:00:00 UT
    ut_hour = local_time_to_ut_hour(14, 30, 0, 5.5)
    assert abs(ut_hour - 9.0) < 0.01


def test_ayanamsa_1990():
    """Ayanamsa for 1990-05-15 should be approximately 23.72°."""
    # 14:30 IST → 09:00 UT
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    ayanamsa = get_ayanamsa(jd)
    assert 23.5 < ayanamsa < 24.0, f"Ayanamsa {ayanamsa} not in expected range"


def test_planet_positions():
    """Test that all 9 planets are computed."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)

    assert len(positions) == 9
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
                 "Venus", "Saturn", "Rahu", "Ketu"]:
        assert name in positions
        assert 0 <= positions[name]["longitude"] < 360


def test_rahu_ketu_opposition():
    """Rahu and Ketu must be exactly 180° apart."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)

    rahu_lon = positions["Rahu"]["longitude"]
    ketu_lon = positions["Ketu"]["longitude"]
    diff = abs(rahu_lon - ketu_lon)
    # Should be exactly 180 (or 360-180=180)
    assert abs(diff - 180.0) < 0.01 or abs(diff - 180.0 + 360) < 0.01


def test_house_cusps():
    """Test that 12 house cusps are returned."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    cusps, ascmc = compute_houses(jd, 28.6139, 77.2090)

    assert len(cusps) == 12
    for cusp in cusps:
        assert 0 <= cusp < 360
    # ascmc[0] is the ascendant
    assert 0 <= ascmc[0] < 360
