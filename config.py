"""Global configuration for the Vedic Jyotish Chart API."""

import swisseph as swe

# Ayanamsa: Lahiri (Chitrapaksha) — standard in Indian Jyotish
AYANAMSA = swe.SIDM_LAHIRI

# House system: Equal ('E') is default; Sripati ('B') available as option
DEFAULT_HOUSE_SYSTEM = b"E"
SRIPATI_HOUSE_SYSTEM = b"B"

# Ephemeris flags
SIDEREAL_FLAGS = swe.FLG_SIDEREAL | swe.FLG_SPEED

# Node type: Mean node for Rahu (traditional Jyotish standard)
RAHU_BODY = swe.MEAN_NODE


def init_swisseph():
    """Initialize Swiss Ephemeris with Lahiri ayanamsa."""
    swe.set_sid_mode(AYANAMSA)
