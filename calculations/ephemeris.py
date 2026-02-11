"""Swiss Ephemeris wrapper — Julian day, planetary positions, house cusps."""
from __future__ import annotations

import swisseph as swe

from config import SIDEREAL_FLAGS, RAHU_BODY, init_swisseph
from constants.grahas import GRAHA_BODIES

init_swisseph()


def datetime_to_jd(year: int, month: int, day: int,
                   hour: float = 0.0) -> float:
    """Convert date + fractional hour (UT) to Julian Day number."""
    return swe.julday(year, month, day, hour)


def local_time_to_ut_hour(hour: int, minute: int, second: int,
                          tz_offset: float) -> tuple[int, int, int, float]:
    """Convert local time + timezone offset to UT date components.

    Returns (year_adj, month_adj, day_adj, ut_hour) — but since we only
    adjust the hour, the caller must handle date rollover if needed.
    For simplicity, returns the UT fractional hour. The caller should
    compute JD using the original date and this UT hour.
    """
    ut_hour = hour + minute / 60.0 + second / 3600.0 - tz_offset
    return ut_hour


def compute_planet_position(jd: float, planet_id: int) -> dict:
    """Compute sidereal position for a single planet.

    Returns dict with keys: longitude, latitude, distance, speed_long,
    speed_lat, speed_dist.
    """
    result, ret_flags = swe.calc_ut(jd, planet_id, SIDEREAL_FLAGS)
    return {
        "longitude": result[0],
        "latitude": result[1],
        "distance": result[2],
        "speed_long": result[3],
        "speed_lat": result[4],
        "speed_dist": result[5],
    }


def compute_all_planets(jd: float) -> dict[str, dict]:
    """Compute sidereal positions for all 9 grahas.

    Ketu is derived from Rahu (180° opposite).
    """
    positions = {}

    for name, body_id in GRAHA_BODIES.items():
        positions[name] = compute_planet_position(jd, body_id)

    # Derive Ketu from Rahu
    rahu = positions["Rahu"]
    positions["Ketu"] = {
        "longitude": (rahu["longitude"] + 180.0) % 360.0,
        "latitude": -rahu["latitude"],
        "distance": rahu["distance"],
        "speed_long": rahu["speed_long"],
        "speed_lat": rahu["speed_lat"],
        "speed_dist": rahu["speed_dist"],
    }

    return positions


def compute_houses(jd: float, latitude: float, longitude: float,
                   house_system: bytes = b"E") -> tuple[list[float], list[float]]:
    """Compute house cusps and ascendant/MC.

    Returns:
        cusps: list of 12 house cusp longitudes (sidereal)
        ascmc: [ascendant, mc, armc, vertex, equatorial_asc, ...]
    """
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude,
                                  house_system, SIDEREAL_FLAGS)
    return list(cusps), list(ascmc)


def get_ayanamsa(jd: float) -> float:
    """Get the ayanamsa value for a given Julian Day."""
    return swe.get_ayanamsa_ut(jd)


def compute_sunrise(jd: float, latitude: float, longitude: float) -> float:
    """Compute sunrise JD (UT) for the day containing the given JD.

    Uses disc-center sunrise (standard for Jyotish).

    Args:
        jd: Julian Day number (UT) — typically start of the local day.
        latitude: Geographic latitude.
        longitude: Geographic longitude (east positive).

    Returns:
        Julian Day of sunrise in UT.
    """
    geopos = (longitude, latitude, 0.0)
    res, tret = swe.rise_trans(
        jd, swe.SUN, swe.CALC_RISE, geopos, 0.0, 0.0, swe.FLG_SWIEPH
    )
    return tret[0]
