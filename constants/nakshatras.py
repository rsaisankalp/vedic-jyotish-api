"""27 Nakshatras and pada calculation."""

# Each nakshatra spans 13°20' (13.3333°)
NAKSHATRA_SPAN = 13.333333333333334  # 360 / 27

# Each pada spans 3°20' (3.3333°)
PADA_SPAN = 3.333333333333333  # 360 / 108

NAKSHATRA_NAMES = {
    1: "Ashwini",
    2: "Bharani",
    3: "Krittika",
    4: "Rohini",
    5: "Mrigashira",
    6: "Ardra",
    7: "Punarvasu",
    8: "Pushya",
    9: "Ashlesha",
    10: "Magha",
    11: "Purva Phalguni",
    12: "Uttara Phalguni",
    13: "Hasta",
    14: "Chitra",
    15: "Swati",
    16: "Vishakha",
    17: "Anuradha",
    18: "Jyeshtha",
    19: "Moola",
    20: "Purva Ashadha",
    21: "Uttara Ashadha",
    22: "Shravana",
    23: "Dhanishtha",
    24: "Shatabhisha",
    25: "Purva Bhadrapada",
    26: "Uttara Bhadrapada",
    27: "Revati",
}

# Nakshatra lords for Vimshottari Dasha
NAKSHATRA_LORDS = {
    1: "Ketu",       # Ashwini
    2: "Venus",      # Bharani
    3: "Sun",        # Krittika
    4: "Moon",       # Rohini
    5: "Mars",       # Mrigashira
    6: "Rahu",       # Ardra
    7: "Jupiter",    # Punarvasu
    8: "Saturn",     # Pushya
    9: "Mercury",    # Ashlesha
    10: "Ketu",      # Magha
    11: "Venus",     # Purva Phalguni
    12: "Sun",       # Uttara Phalguni
    13: "Moon",      # Hasta
    14: "Mars",      # Chitra
    15: "Rahu",      # Swati
    16: "Jupiter",   # Vishakha
    17: "Saturn",    # Anuradha
    18: "Mercury",   # Jyeshtha
    19: "Ketu",      # Moola
    20: "Venus",     # Purva Ashadha
    21: "Sun",       # Uttara Ashadha
    22: "Moon",      # Shravana
    23: "Mars",      # Dhanishtha
    24: "Rahu",      # Shatabhisha
    25: "Jupiter",   # Purva Bhadrapada
    26: "Saturn",    # Uttara Bhadrapada
    27: "Mercury",   # Revati
}


def longitude_to_nakshatra(longitude: float) -> int:
    """Convert sidereal longitude (0–360) to nakshatra number (1–27)."""
    return int(longitude / NAKSHATRA_SPAN) % 27 + 1


def longitude_to_pada(longitude: float) -> int:
    """Convert sidereal longitude (0–360) to pada (1–4) within its nakshatra."""
    nak_start = (longitude_to_nakshatra(longitude) - 1) * NAKSHATRA_SPAN
    offset = longitude - nak_start
    return int(offset / PADA_SPAN) % 4 + 1


def nakshatra_traversed_fraction(longitude: float) -> float:
    """Fraction of the current nakshatra already traversed (0.0–1.0)."""
    nak_start = (longitude_to_nakshatra(longitude) - 1) * NAKSHATRA_SPAN
    offset = longitude - nak_start
    return offset / NAKSHATRA_SPAN
