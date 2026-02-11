"""Tests for graha position calculations."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calculations.ephemeris import datetime_to_jd, compute_all_planets, compute_houses
from calculations.grahas import compute_graha_positions
from constants.grahas import GRAHA_NAMES


def test_graha_positions_count():
    """All 9 grahas should be computed."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, _ = compute_houses(jd, 28.6139, 77.2090)
    grahas = compute_graha_positions(positions, cusps)

    assert len(grahas) == 9
    graha_names = [g["graha"] for g in grahas]
    for name in GRAHA_NAMES:
        assert name in graha_names


def test_graha_fields():
    """Each graha should have all required fields."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, _ = compute_houses(jd, 28.6139, 77.2090)
    grahas = compute_graha_positions(positions, cusps)

    required_fields = [
        "graha", "graha_sanskrit", "longitude", "rashi", "rashi_name",
        "rashi_lord", "degree_in_rashi", "nakshatra", "nakshatra_name",
        "nakshatra_lord", "pada", "house", "retrograde", "speed",
    ]

    for graha in grahas:
        for field in required_fields:
            assert field in graha, f"Missing field {field} for {graha['graha']}"


def test_rashi_range():
    """Rashi should be 1–12 for all grahas."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, _ = compute_houses(jd, 28.6139, 77.2090)
    grahas = compute_graha_positions(positions, cusps)

    for g in grahas:
        assert 1 <= g["rashi"] <= 12, f"{g['graha']} rashi={g['rashi']}"
        assert 1 <= g["nakshatra"] <= 27
        assert 1 <= g["pada"] <= 4
        assert 1 <= g["house"] <= 12


def test_rahu_ketu_retrograde():
    """Rahu and Ketu should always be marked retrograde."""
    jd = datetime_to_jd(1990, 5, 15, 9.0)
    positions = compute_all_planets(jd)
    cusps, _ = compute_houses(jd, 28.6139, 77.2090)
    grahas = compute_graha_positions(positions, cusps)

    graha_dict = {g["graha"]: g for g in grahas}
    assert graha_dict["Rahu"]["retrograde"] is True
    assert graha_dict["Ketu"]["retrograde"] is True
