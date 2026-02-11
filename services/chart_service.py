"""Chart service — orchestrates full chart computation."""
from __future__ import annotations

from datetime import datetime

from calculations.ephemeris import (
    datetime_to_jd, local_time_to_ut_hour, compute_all_planets,
    compute_houses, get_ayanamsa,
)
from calculations.lagna import compute_lagna
from calculations.bhavas import compute_bhavas
from calculations.grahas import compute_graha_positions
from calculations.divisional import compute_all_divisional_charts, compute_divisional_chart
from calculations.dasha import compute_mahadasha
from calculations.panchanga import compute_panchanga
from calculations.ashtakavarga import (
    compute_bhinnashtakavarga, compute_sarvashtakavarga, format_ashtakavarga,
)
from config import DEFAULT_HOUSE_SYSTEM


def _parse_birth_input(date_str: str, time_str: str, tz_offset: float,
                       latitude: float, longitude: float) -> tuple:
    """Parse birth input strings into computation-ready values.

    Returns: (jd, birth_dt, year, month, day, hour, minute, second)
    """
    year, month, day = map(int, date_str.split("-"))
    hour, minute, second = map(int, time_str.split(":"))

    ut_hour = local_time_to_ut_hour(hour, minute, second, tz_offset)

    # Handle date rollover for UT conversion
    ut_day = day
    ut_month = month
    ut_year = year
    if ut_hour < 0:
        ut_hour += 24
        ut_day -= 1
        # Simplified: doesn't handle month boundaries perfectly
        # but swisseph handles this internally via JD
    elif ut_hour >= 24:
        ut_hour -= 24
        ut_day += 1

    jd = datetime_to_jd(ut_year, ut_month, ut_day, ut_hour)

    # Birth datetime in local time (for dasha reference)
    birth_dt = datetime(year, month, day, hour, minute, second)

    return jd, birth_dt


def compute_full_chart(name: str | None, date_str: str, time_str: str,
                       latitude: float, longitude: float,
                       tz_offset: float) -> dict:
    """Compute a complete Vedic birth chart.

    Returns a dict matching the ChartResponse schema.
    """
    jd, birth_dt = _parse_birth_input(date_str, time_str, tz_offset,
                                       latitude, longitude)

    # Ayanamsa
    ayanamsa = get_ayanamsa(jd)

    # Planet positions
    planet_positions = compute_all_planets(jd)

    # House cusps
    cusps, ascmc = compute_houses(jd, latitude, longitude, DEFAULT_HOUSE_SYSTEM)
    ascendant_longitude = ascmc[0]

    # Lagna
    lagna = compute_lagna(ascendant_longitude)

    # Bhavas
    bhavas = compute_bhavas(cusps, ascendant_longitude)

    # Graha positions
    grahas = compute_graha_positions(planet_positions, cusps)

    # Divisional charts
    divisional_charts = compute_all_divisional_charts(
        planet_positions, ascendant_longitude
    )

    # Vimshottari Dasha (3 levels)
    moon_longitude = planet_positions["Moon"]["longitude"]
    dasha = compute_mahadasha(moon_longitude, birth_dt, levels=3)

    # Panchanga
    sun_longitude = planet_positions["Sun"]["longitude"]
    panchanga = compute_panchanga(sun_longitude, moon_longitude, jd, tz_offset,
                                   latitude, longitude)

    # Ashtakavarga
    bav = compute_bhinnashtakavarga(planet_positions, ascendant_longitude)
    sav = compute_sarvashtakavarga(bav)
    ashtakavarga = format_ashtakavarga(bav, sav)

    return {
        "name": name,
        "birth_data": {
            "date": date_str,
            "time": time_str,
            "latitude": latitude,
            "longitude": longitude,
            "timezone_offset": tz_offset,
        },
        "ayanamsa": round(ayanamsa, 6),
        "lagna": lagna,
        "grahas": grahas,
        "bhavas": bhavas,
        "divisional_charts": divisional_charts,
        "dasha": dasha,
        "panchanga": panchanga,
        "ashtakavarga": ashtakavarga,
    }


def compute_single_divisional(date_str: str, time_str: str,
                               latitude: float, longitude: float,
                               tz_offset: float,
                               chart_type: str) -> dict:
    """Compute a single divisional chart."""
    jd, _ = _parse_birth_input(date_str, time_str, tz_offset,
                                latitude, longitude)

    planet_positions = compute_all_planets(jd)
    cusps, ascmc = compute_houses(jd, latitude, longitude, DEFAULT_HOUSE_SYSTEM)
    ascendant_longitude = ascmc[0]

    return compute_divisional_chart(planet_positions, ascendant_longitude, chart_type)


def compute_dasha_only(date_str: str, time_str: str,
                       latitude: float, longitude: float,
                       tz_offset: float,
                       levels: int = 3) -> list[dict]:
    """Compute only the Vimshottari Dasha periods."""
    jd, birth_dt = _parse_birth_input(date_str, time_str, tz_offset,
                                       latitude, longitude)

    planet_positions = compute_all_planets(jd)
    moon_longitude = planet_positions["Moon"]["longitude"]

    return compute_mahadasha(moon_longitude, birth_dt, levels=levels)
