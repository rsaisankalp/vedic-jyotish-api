"""Ascendant (Lagna) calculation."""

from constants.rashis import longitude_to_rashi, longitude_to_rashi_degree, RASHI_NAMES
from constants.nakshatras import (
    longitude_to_nakshatra, longitude_to_pada, NAKSHATRA_NAMES,
)


def compute_lagna(ascendant_longitude: float) -> dict:
    """Compute lagna details from the ascendant longitude.

    Args:
        ascendant_longitude: Sidereal longitude of the ascendant (from house cusps).

    Returns:
        Dict with rashi, degree, nakshatra, pada info.
    """
    rashi = longitude_to_rashi(ascendant_longitude)
    nakshatra = longitude_to_nakshatra(ascendant_longitude)

    return {
        "longitude": round(ascendant_longitude, 4),
        "rashi": rashi,
        "rashi_name": RASHI_NAMES[rashi],
        "degree_in_rashi": round(longitude_to_rashi_degree(ascendant_longitude), 4),
        "nakshatra": nakshatra,
        "nakshatra_name": NAKSHATRA_NAMES[nakshatra],
        "pada": longitude_to_pada(ascendant_longitude),
    }
