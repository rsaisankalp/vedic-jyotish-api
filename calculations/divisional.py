"""Divisional chart (Varga) calculations: D1–D60."""
from __future__ import annotations

from constants.rashis import longitude_to_rashi, RASHI_NAMES
from constants.divisional_mappings import TRIMSAMSA_ODD, TRIMSAMSA_EVEN, TRIMSAMSA_SIGN


def _d1_sign(longitude: float) -> int:
    """D1 (Rashi chart) — same as birth rashi."""
    return longitude_to_rashi(longitude)


def _d2_sign(longitude: float) -> int:
    """D2 (Hora) — 2 divisions of 15° each.

    Odd sign: first half → Leo (5), second half → Cancer (4).
    Even sign: first half → Cancer (4), second half → Leo (5).
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    is_odd = rashi % 2 == 1

    if degree < 15:
        return 5 if is_odd else 4
    else:
        return 4 if is_odd else 5


def _d3_sign(longitude: float) -> int:
    """D3 (Drekkana) — 3 divisions of 10° each.

    Part 1 (0–10°): same sign
    Part 2 (10–20°): 5th from sign
    Part 3 (20–30°): 9th from sign
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30

    if degree < 10:
        return rashi
    elif degree < 20:
        return (rashi - 1 + 4) % 12 + 1  # 5th from sign
    else:
        return (rashi - 1 + 8) % 12 + 1  # 9th from sign


def _d7_sign(longitude: float) -> int:
    """D7 (Saptamsa) — 7 divisions of 4°17'8.57" each.

    Odd sign: count from same sign.
    Even sign: count from 7th from sign.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    part = int(degree / (30 / 7))  # 0–6
    is_odd = rashi % 2 == 1

    if is_odd:
        return (rashi - 1 + part) % 12 + 1
    else:
        return (rashi - 1 + 6 + part) % 12 + 1


def _d9_sign(longitude: float) -> int:
    """D9 (Navamsa) — 9 divisions of 3°20' each.

    The navamsa sign is determined by the absolute pada number.
    Each pada of 3°20' maps sequentially through the 12 signs,
    starting from Aries for fire signs, Cancer for water, Libra for air,
    Capricorn for earth.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    part = int(degree / (30 / 9))  # 0–8

    # Starting sign based on element of rashi
    if rashi in (1, 5, 9):       # Fire
        start = 1
    elif rashi in (2, 6, 10):    # Earth
        start = 10
    elif rashi in (3, 7, 11):    # Air
        start = 7
    else:                         # Water (4, 8, 12)
        start = 4

    return (start - 1 + part) % 12 + 1


def _d10_sign(longitude: float) -> int:
    """D10 (Dasamsa) — 10 divisions of 3° each.

    Odd sign: count from same sign.
    Even sign: count from 9th from sign.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    part = int(degree / 3)  # 0–9
    is_odd = rashi % 2 == 1

    if is_odd:
        return (rashi - 1 + part) % 12 + 1
    else:
        return (rashi - 1 + 8 + part) % 12 + 1


def _d12_sign(longitude: float) -> int:
    """D12 (Dwadasamsa) — 12 divisions of 2°30' each.

    Count from the same sign.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    part = int(degree / 2.5)  # 0–11

    return (rashi - 1 + part) % 12 + 1


def _d30_sign(longitude: float) -> int:
    """D30 (Trimsamsa) — unequal divisions based on Parashara's table.

    Odd signs and even signs have different division schemes.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    is_odd = rashi % 2 == 1

    table = TRIMSAMSA_ODD if is_odd else TRIMSAMSA_EVEN
    cumulative = 0
    for span, lord in table:
        cumulative += span
        if degree < cumulative:
            return TRIMSAMSA_SIGN[lord]

    # Fallback (should not reach here)
    return TRIMSAMSA_SIGN[table[-1][1]]


def _d60_sign(longitude: float) -> int:
    """D60 (Shashtiamsa) — 60 divisions of 0°30' each.

    Odd sign: count forward from the same sign.
    Even sign: count backward from the same sign.
    """
    rashi = longitude_to_rashi(longitude)
    degree = longitude % 30
    part = int(degree / 0.5)  # 0–59
    is_odd = rashi % 2 == 1

    if is_odd:
        return (rashi - 1 + part) % 12 + 1
    else:
        return (rashi - 1 - part) % 12 + 1


# Dispatcher
_DIVISIONAL_FUNCS = {
    "D1": _d1_sign,
    "D2": _d2_sign,
    "D3": _d3_sign,
    "D7": _d7_sign,
    "D9": _d9_sign,
    "D10": _d10_sign,
    "D12": _d12_sign,
    "D30": _d30_sign,
    "D60": _d60_sign,
}


def compute_divisional_chart(planet_positions: dict[str, dict],
                             ascendant_longitude: float,
                             chart_type: str = "D9") -> dict:
    """Compute a divisional chart for all grahas and lagna.

    Args:
        planet_positions: Output of ephemeris.compute_all_planets().
        ascendant_longitude: Sidereal longitude of the ascendant.
        chart_type: One of D1, D2, D3, D7, D9, D10, D12, D30, D60.

    Returns:
        Dict with chart_type, lagna info, and list of graha placements.
    """
    func = _DIVISIONAL_FUNCS.get(chart_type)
    if func is None:
        raise ValueError(f"Unsupported divisional chart: {chart_type}")

    lagna_sign = func(ascendant_longitude)

    grahas = []
    from constants.grahas import GRAHA_NAMES
    for name in GRAHA_NAMES:
        lon = planet_positions[name]["longitude"]
        sign = func(lon)
        grahas.append({
            "graha": name,
            "rashi": sign,
            "rashi_name": RASHI_NAMES[sign],
        })

    return {
        "chart_type": chart_type,
        "lagna": {
            "rashi": lagna_sign,
            "rashi_name": RASHI_NAMES[lagna_sign],
        },
        "grahas": grahas,
    }


def compute_all_divisional_charts(planet_positions: dict[str, dict],
                                  ascendant_longitude: float) -> list[dict]:
    """Compute all 9 supported divisional charts."""
    charts = []
    for chart_type in _DIVISIONAL_FUNCS:
        charts.append(
            compute_divisional_chart(planet_positions, ascendant_longitude, chart_type)
        )
    return charts
