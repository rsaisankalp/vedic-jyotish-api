"""Vimshottari Dasha sequence and durations."""

# Total Vimshottari Dasha cycle = 120 years
VIMSHOTTARI_TOTAL_YEARS = 120

# Dasha sequence and durations (in years)
VIMSHOTTARI_SEQUENCE = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17),
]

# Quick lookup: graha name → duration in years
DASHA_DURATIONS = {name: years for name, years in VIMSHOTTARI_SEQUENCE}

# Ordered list of graha names in dasha sequence
DASHA_ORDER = [name for name, _ in VIMSHOTTARI_SEQUENCE]
