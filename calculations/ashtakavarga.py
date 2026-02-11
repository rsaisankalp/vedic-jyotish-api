"""Ashtakavarga calculation — Bhinnashtakavarga + Sarvashtakavarga."""
from __future__ import annotations

from constants.rashis import longitude_to_rashi, RASHI_NAMES
from constants.ashtakavarga_tables import BINDU_TABLES, ASHTAKAVARGA_PLANETS


def _rashi_distance(from_rashi: int, to_rashi: int) -> int:
    """House number of to_rashi counted from from_rashi (1-indexed).

    E.g., if from=1, to=1 → 1; from=1, to=3 → 3; from=12, to=1 → 2.
    """
    return (to_rashi - from_rashi) % 12 + 1


def compute_bhinnashtakavarga(planet_positions: dict[str, dict],
                               ascendant_longitude: float) -> dict[str, list[int]]:
    """Compute Bhinnashtakavarga (BAV) for each of the 7 planets.

    Args:
        planet_positions: Output of ephemeris.compute_all_planets().
        ascendant_longitude: Sidereal longitude of the ascendant.

    Returns:
        Dict mapping planet name → list of 12 bindu counts (index 0 = rashi 1).
    """
    # Get rashi positions for all reference points
    rashi_positions = {}
    for planet in ASHTAKAVARGA_PLANETS:
        rashi_positions[planet] = longitude_to_rashi(
            planet_positions[planet]["longitude"]
        )
    rashi_positions["Lagna"] = longitude_to_rashi(ascendant_longitude)

    bav = {}

    for planet in ASHTAKAVARGA_PLANETS:
        bindus = [0] * 12  # index 0 = rashi 1, ..., index 11 = rashi 12
        bindu_table = BINDU_TABLES[planet]

        for ref_name, contributing_houses in bindu_table.items():
            ref_rashi = rashi_positions[ref_name]

            for house in contributing_houses:
                # The target rashi is `house` signs from ref_rashi
                target_rashi = (ref_rashi - 1 + house - 1) % 12 + 1
                bindus[target_rashi - 1] += 1

        bav[planet] = bindus

    return bav


def compute_sarvashtakavarga(bav: dict[str, list[int]]) -> list[int]:
    """Compute Sarvashtakavarga (SAV) — sum of all BAVs.

    Args:
        bav: Output of compute_bhinnashtakavarga().

    Returns:
        List of 12 total bindu counts (index 0 = rashi 1).
    """
    sav = [0] * 12
    for planet, bindus in bav.items():
        for i in range(12):
            sav[i] += bindus[i]
    return sav


def format_ashtakavarga(bav: dict[str, list[int]],
                         sav: list[int]) -> dict:
    """Format ashtakavarga results for API response."""
    formatted_bav = {}
    for planet, bindus in bav.items():
        formatted_bav[planet] = {
            "bindus": bindus,
            "total": sum(bindus),
            "by_rashi": {
                RASHI_NAMES[i + 1]: bindus[i] for i in range(12)
            },
        }

    return {
        "bhinnashtakavarga": formatted_bav,
        "sarvashtakavarga": {
            "bindus": sav,
            "total": sum(sav),
            "by_rashi": {
                RASHI_NAMES[i + 1]: sav[i] for i in range(12)
            },
        },
    }
