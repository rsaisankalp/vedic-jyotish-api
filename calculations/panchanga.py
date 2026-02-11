"""Panchanga calculation — Tithi, Karana, Yoga, Nakshatra, Vara."""

import swisseph as swe

from constants.nakshatras import (
    longitude_to_nakshatra, longitude_to_pada, NAKSHATRA_NAMES, NAKSHATRA_LORDS,
)

# Vara (weekday) names — 0=Monday in Python's weekday(), but in Jyotish
# we map from Julian Day where day 0 = Monday
VARA_NAMES = {
    0: "Ravivara",     # Sunday
    1: "Somavara",     # Monday
    2: "Mangalavara",  # Tuesday
    3: "Budhavara",    # Wednesday
    4: "Guruvara",     # Thursday
    5: "Shukravara",   # Friday
    6: "Shanivara",    # Saturday
}

VARA_ENGLISH = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}

# 30 Tithis
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

# 11 Karanas (half-tithis), 4 fixed + 7 repeating
KARANA_FIXED = ["Kimstughna", "Shakuni", "Chatushpada", "Nagava"]
KARANA_REPEATING = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]

# 27 Yogas
YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]


def compute_panchanga(sun_longitude: float, moon_longitude: float,
                      jd: float, tz_offset: float = 0.0,
                      latitude: float = 0.0, longitude: float = 0.0) -> dict:
    """Compute the five elements of Panchanga.

    Args:
        sun_longitude: Sidereal longitude of the Sun.
        moon_longitude: Sidereal longitude of the Moon.
        jd: Julian Day number (UT).
        tz_offset: Timezone offset in hours from UTC.
        latitude: Geographic latitude (for sunrise-based Vara).
        longitude: Geographic longitude (for sunrise-based Vara).

    Returns:
        Dict with tithi, karana, yoga, nakshatra, vara details.
    """
    # 1. Tithi — based on Moon-Sun angular distance
    moon_sun_diff = (moon_longitude - sun_longitude) % 360
    tithi_num = int(moon_sun_diff / 12)  # 0–29
    tithi_name = TITHI_NAMES[tithi_num]
    paksha = "Shukla" if tithi_num < 15 else "Krishna"

    # 2. Karana — half of a tithi (60 karanas in a lunar month)
    karana_num = int(moon_sun_diff / 6)  # 0–59
    if karana_num == 0:
        karana_name = KARANA_FIXED[0]  # Kimstughna
    elif karana_num == 57:
        karana_name = KARANA_FIXED[1]  # Shakuni
    elif karana_num == 58:
        karana_name = KARANA_FIXED[2]  # Chatushpada
    elif karana_num == 59:
        karana_name = KARANA_FIXED[3]  # Nagava
    else:
        karana_name = KARANA_REPEATING[(karana_num - 1) % 7]

    # 3. Yoga — based on sum of Sun + Moon longitudes
    yoga_sum = (sun_longitude + moon_longitude) % 360
    yoga_num = int(yoga_sum / (360 / 27))  # 0–26
    yoga_name = YOGA_NAMES[yoga_num]

    # 4. Nakshatra — Moon's nakshatra
    nak = longitude_to_nakshatra(moon_longitude)

    # 5. Vara — weekday based on Jyotish sunrise-to-sunrise convention
    # In Jyotish, the day (Vara) runs from sunrise to sunrise, not midnight.
    # If birth is before sunrise, the Vara is the previous calendar day's weekday.
    from calculations.ephemeris import compute_sunrise

    local_jd = jd + tz_offset / 24.0
    # Compute sunrise for the calendar date of birth
    # Search for sunrise starting from ~midnight UT of the local date
    jd_midnight_ut = jd - (jd % 1) + 0.5  # noon JD, then back to midnight
    # More robust: use the local midnight in UT
    local_midnight_jd = int(local_jd + 0.5) - 0.5  # local midnight JD
    local_midnight_ut = local_midnight_jd - tz_offset / 24.0
    sunrise_jd = compute_sunrise(local_midnight_ut, latitude, longitude)

    if jd < sunrise_jd:
        # Birth is before sunrise — use previous day's weekday
        vara_jd = local_jd - 1.0
    else:
        vara_jd = local_jd

    # floor(JD + 1.5) % 7 gives: 0=Sun, 1=Mon, 2=Tue, ..., 6=Sat
    vara_idx = int(vara_jd + 1.5) % 7

    # Compute sunrise time in local hours for display
    # Use swe.revjul to properly extract UT hours, then add tz offset
    _, _, _, sunrise_ut_hours = swe.revjul(sunrise_jd)
    sunrise_local_hours = sunrise_ut_hours + tz_offset
    if sunrise_local_hours >= 24:
        sunrise_local_hours -= 24
    elif sunrise_local_hours < 0:
        sunrise_local_hours += 24
    sunrise_h = int(sunrise_local_hours)
    sunrise_m = int((sunrise_local_hours - sunrise_h) * 60)
    sunrise_s = int(((sunrise_local_hours - sunrise_h) * 60 - sunrise_m) * 60)
    sunrise_str = f"{sunrise_h:02d}:{sunrise_m:02d}:{sunrise_s:02d}"

    return {
        "sunrise": sunrise_str,
        "tithi": {
            "number": tithi_num + 1,
            "name": tithi_name,
            "paksha": paksha,
        },
        "karana": {
            "number": karana_num + 1,
            "name": karana_name,
        },
        "yoga": {
            "number": yoga_num + 1,
            "name": yoga_name,
        },
        "nakshatra": {
            "number": nak,
            "name": NAKSHATRA_NAMES[nak],
            "lord": NAKSHATRA_LORDS[nak],
            "pada": longitude_to_pada(moon_longitude),
        },
        "vara": {
            "name": VARA_NAMES[vara_idx],
            "english": VARA_ENGLISH[vara_idx],
        },
    }
