"""Graha (planet) position computation with rashi, nakshatra, house placement."""
from __future__ import annotations

from constants.rashis import (
    longitude_to_rashi, longitude_to_rashi_degree, RASHI_NAMES, RASHI_LORDS,
)
from constants.nakshatras import (
    longitude_to_nakshatra, longitude_to_pada, NAKSHATRA_NAMES, NAKSHATRA_LORDS,
)
from constants.grahas import (
    GRAHA_NAMES, GRAHA_SANSKRIT, EXALTATION, DEBILITATION, OWN_SIGNS,
)
from calculations.bhavas import get_house_for_longitude


def _dignity(graha: str, rashi: int) -> str | None:
    """Determine the dignity of a graha in a rashi."""
    if EXALTATION.get(graha) == rashi:
        return "exalted"
    if DEBILITATION.get(graha) == rashi:
        return "debilitated"
    if rashi in OWN_SIGNS.get(graha, set()):
        return "own_sign"
    return None


def compute_graha_positions(planet_positions: dict[str, dict],
                            cusps: list[float]) -> list[dict]:
    """Compute detailed position info for all 9 grahas.

    Args:
        planet_positions: Output of ephemeris.compute_all_planets().
        cusps: List of 12 house cusp longitudes.

    Returns:
        List of graha position dicts.
    """
    results = []

    for name in GRAHA_NAMES:
        pos = planet_positions[name]
        lon = pos["longitude"]
        speed = pos["speed_long"]

        rashi = longitude_to_rashi(lon)
        nakshatra = longitude_to_nakshatra(lon)

        # Rahu and Ketu are always considered retrograde in Jyotish
        is_retrograde = speed < 0 or name in ("Rahu", "Ketu")

        results.append({
            "graha": name,
            "graha_sanskrit": GRAHA_SANSKRIT[name],
            "longitude": round(lon, 4),
            "rashi": rashi,
            "rashi_name": RASHI_NAMES[rashi],
            "rashi_lord": RASHI_LORDS[rashi],
            "degree_in_rashi": round(longitude_to_rashi_degree(lon), 4),
            "nakshatra": nakshatra,
            "nakshatra_name": NAKSHATRA_NAMES[nakshatra],
            "nakshatra_lord": NAKSHATRA_LORDS[nakshatra],
            "pada": longitude_to_pada(lon),
            "house": get_house_for_longitude(lon, cusps),
            "retrograde": is_retrograde,
            "speed": round(speed, 6),
            "dignity": _dignity(name, rashi),
        })

    return results
