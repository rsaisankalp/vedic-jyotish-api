"""House (Bhava) cusp calculation."""
from __future__ import annotations

from constants.rashis import longitude_to_rashi, RASHI_NAMES, RASHI_LORDS


def compute_bhavas(cusps: list[float], ascendant_longitude: float) -> list[dict]:
    """Compute bhava (house) details from house cusps.

    Args:
        cusps: List of 12 house cusp longitudes (sidereal).
        ascendant_longitude: The ascendant longitude.

    Returns:
        List of 12 bhava dicts with house number, cusp longitude, rashi, lord.
    """
    bhavas = []
    for i in range(12):
        cusp_long = cusps[i]
        rashi = longitude_to_rashi(cusp_long)
        bhavas.append({
            "house": i + 1,
            "cusp_longitude": round(cusp_long, 4),
            "rashi": rashi,
            "rashi_name": RASHI_NAMES[rashi],
            "lord": RASHI_LORDS[rashi],
        })
    return bhavas


def get_house_for_longitude(longitude: float, cusps: list[float]) -> int:
    """Determine which house (1–12) a given longitude falls in.

    Uses the cusp boundaries: a planet is in house N if its longitude
    is between cusp N and cusp N+1.
    """
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]

        if cusp_start < cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # Wraps around 360°/0°
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1

    # Fallback: equal house from ascendant
    return int(((longitude - cusps[0]) % 360) / 30) + 1
