"""Tests for Vimshottari Dasha calculation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

from calculations.dasha import compute_mahadasha
from calculations.ephemeris import datetime_to_jd, compute_all_planets


def test_mahadasha_count():
    """Should return exactly 9 Mahadasha periods."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    moon_lon = positions["Moon"]["longitude"]
    birth_dt = datetime(1990, 5, 15, 14, 30, 0)

    dashas = compute_mahadasha(moon_lon, birth_dt, levels=1)
    assert len(dashas) == 9


def test_mahadasha_total_approximately_120_years():
    """Total duration of all Mahadashas should be <= 120 years.

    The first dasha is partially elapsed at birth, so the total from birth
    to end is 120 minus the elapsed portion.
    """
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    moon_lon = positions["Moon"]["longitude"]
    birth_dt = datetime(1990, 5, 15, 14, 30, 0)

    dashas = compute_mahadasha(moon_lon, birth_dt, levels=1)
    total_years = sum(d["duration_years"] for d in dashas)
    # Total should be <= 120 (first dasha is partial) and > 100
    assert 100 < total_years <= 120.01


def test_antardasha_count():
    """Each Mahadasha should have 9 Antardashas at level 2."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    moon_lon = positions["Moon"]["longitude"]
    birth_dt = datetime(1990, 5, 15, 14, 30, 0)

    dashas = compute_mahadasha(moon_lon, birth_dt, levels=2)
    for d in dashas:
        assert "antardasha" in d
        assert len(d["antardasha"]) == 9


def test_antardasha_duration_sums():
    """Antardasha durations should sum to Mahadasha duration."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    moon_lon = positions["Moon"]["longitude"]
    birth_dt = datetime(1990, 5, 15, 14, 30, 0)

    dashas = compute_mahadasha(moon_lon, birth_dt, levels=2)
    for d in dashas:
        antar_total = sum(a["duration_years"] for a in d["antardasha"])
        assert abs(antar_total - d["duration_years"]) < 0.01


def test_pratyantardasha():
    """Level 3 should include pratyantardasha."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    moon_lon = positions["Moon"]["longitude"]
    birth_dt = datetime(1990, 5, 15, 14, 30, 0)

    dashas = compute_mahadasha(moon_lon, birth_dt, levels=3)
    # Check that the first antardasha of the first mahadasha has pratyantardasha
    first_antar = dashas[0]["antardasha"][0]
    assert "pratyantardasha" in first_antar
    assert len(first_antar["pratyantardasha"]) == 9
