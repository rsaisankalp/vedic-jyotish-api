"""Divisional chart (Varga) division rules.

Each divisional chart divides a sign into N equal parts.
The resulting sign is determined by the division rules below.
"""

# Supported divisional charts and their division factors
DIVISIONAL_CHARTS = {
    "D1": 1,    # Rashi (birth chart)
    "D2": 2,    # Hora
    "D3": 3,    # Drekkana
    "D7": 7,    # Saptamsa
    "D9": 9,    # Navamsa
    "D10": 10,  # Dasamsa
    "D12": 12,  # Dwadasamsa
    "D30": 30,  # Trimsamsa
    "D60": 60,  # Shashtiamsa
}

# D2 (Hora): odd signs → Sun (Leo) / Moon (Cancer) based on half
# First half of odd sign → Leo (5), second half → Cancer (4)
# First half of even sign → Cancer (4), second half → Leo (5)

# D3 (Drekkana): 3 parts of 10° each
# Part 1 → same sign, Part 2 → 5th from it, Part 3 → 9th from it

# D30 (Trimsamsa) degrees and lords for odd signs (per Parashara)
# For even signs, the order is reversed
TRIMSAMSA_ODD = [
    (5, "Mars"),      # 0–5°
    (5, "Saturn"),    # 5–10°
    (8, "Jupiter"),   # 10–18°
    (7, "Mercury"),   # 18–25°
    (5, "Venus"),     # 25–30°
]

TRIMSAMSA_EVEN = [
    (5, "Venus"),     # 0–5°
    (7, "Mercury"),   # 5–12°
    (8, "Jupiter"),   # 12–20°
    (5, "Saturn"),    # 20–25°
    (5, "Mars"),      # 25–30°
]

# Trimsamsa lord → sign mapping
TRIMSAMSA_SIGN = {
    "Mars": 1,       # Aries
    "Saturn": 11,    # Aquarius
    "Jupiter": 9,    # Sagittarius
    "Mercury": 3,    # Gemini
    "Venus": 7,      # Libra
}
