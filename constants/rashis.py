"""12 Rashis (zodiac signs) and helpers."""

RASHI_NAMES = {
    1: "Mesha",       # Aries
    2: "Vrishabha",   # Taurus
    3: "Mithuna",     # Gemini
    4: "Karka",       # Cancer
    5: "Simha",       # Leo
    6: "Kanya",       # Virgo
    7: "Tula",        # Libra
    8: "Vrischika",   # Scorpio
    9: "Dhanu",       # Sagittarius
    10: "Makara",     # Capricorn
    11: "Kumbha",     # Aquarius
    12: "Meena",      # Pisces
}

RASHI_LORDS = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Moon",
    5: "Sun",
    6: "Mercury",
    7: "Venus",
    8: "Mars",
    9: "Jupiter",
    10: "Saturn",
    11: "Saturn",
    12: "Jupiter",
}

# Element classification
FIRE_SIGNS = {1, 5, 9}
EARTH_SIGNS = {2, 6, 10}
AIR_SIGNS = {3, 7, 11}
WATER_SIGNS = {4, 8, 12}

# Modality
MOVABLE_SIGNS = {1, 4, 7, 10}      # Chara
FIXED_SIGNS = {2, 5, 8, 11}        # Sthira
DUAL_SIGNS = {3, 6, 9, 12}         # Dwiswabhava


def longitude_to_rashi(longitude: float) -> int:
    """Convert sidereal longitude (0–360) to rashi number (1–12)."""
    return int(longitude / 30) % 12 + 1


def longitude_to_rashi_degree(longitude: float) -> float:
    """Convert sidereal longitude to degree within its rashi (0–30)."""
    return longitude % 30
