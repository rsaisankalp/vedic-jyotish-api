"""Vimshottari Dasha calculation — Mahadasha, Antardasha, Pratyantardasha."""
from __future__ import annotations

from datetime import datetime, timedelta

from constants.nakshatras import (
    longitude_to_nakshatra, nakshatra_traversed_fraction, NAKSHATRA_LORDS,
)
from constants.dashas import (
    VIMSHOTTARI_TOTAL_YEARS, DASHA_DURATIONS, DASHA_ORDER,
)


def _years_to_days(years: float) -> float:
    """Convert years to days (using 365.25 days/year)."""
    return years * 365.25


def _get_dasha_start_index(moon_longitude: float) -> int:
    """Get the index in DASHA_ORDER for the Moon's birth nakshatra lord."""
    nak = longitude_to_nakshatra(moon_longitude)
    lord = NAKSHATRA_LORDS[nak]
    return DASHA_ORDER.index(lord)


def compute_mahadasha(moon_longitude: float,
                      birth_dt: datetime,
                      levels: int = 3) -> list[dict]:
    """Compute Vimshottari Mahadasha periods with optional sub-periods.

    Args:
        moon_longitude: Sidereal longitude of the Moon at birth.
        birth_dt: Birth datetime (UTC or local — used as reference).
        levels: Depth of sub-periods (1=Maha only, 2=+Antar, 3=+Pratyantar).

    Returns:
        List of Mahadasha period dicts, each potentially containing sub-periods.
    """
    # Balance of the first dasha
    fraction_elapsed = nakshatra_traversed_fraction(moon_longitude)
    start_idx = _get_dasha_start_index(moon_longitude)

    first_lord = DASHA_ORDER[start_idx]
    full_duration_years = DASHA_DURATIONS[first_lord]
    remaining_fraction = 1.0 - fraction_elapsed
    first_balance_years = full_duration_years * remaining_fraction

    periods = []
    current_date = birth_dt

    for cycle_offset in range(9):
        idx = (start_idx + cycle_offset) % 9
        lord = DASHA_ORDER[idx]

        if cycle_offset == 0:
            duration_years = first_balance_years
        else:
            duration_years = DASHA_DURATIONS[lord]

        duration_days = _years_to_days(duration_years)
        end_date = current_date + timedelta(days=duration_days)

        period = {
            "lord": lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "duration_years": round(duration_years, 4),
        }

        if levels >= 2:
            period["antardasha"] = _compute_sub_periods(
                lord, current_date, duration_years, levels - 1
            )

        periods.append(period)
        current_date = end_date

    return periods


def _compute_sub_periods(maha_lord: str, start_date: datetime,
                         maha_duration_years: float,
                         remaining_levels: int) -> list[dict]:
    """Compute sub-periods (Antardasha / Pratyantardasha) within a Mahadasha.

    The sub-period sequence starts from the Mahadasha lord itself,
    then proceeds in Vimshottari order.
    """
    start_idx = DASHA_ORDER.index(maha_lord)
    current_date = start_date
    sub_periods = []

    for cycle_offset in range(9):
        idx = (start_idx + cycle_offset) % 9
        sub_lord = DASHA_ORDER[idx]

        # Sub-period duration = (maha_duration * sub_lord_full_duration) / 120
        sub_duration_years = (
            maha_duration_years * DASHA_DURATIONS[sub_lord]
        ) / VIMSHOTTARI_TOTAL_YEARS

        sub_duration_days = _years_to_days(sub_duration_years)
        end_date = current_date + timedelta(days=sub_duration_days)

        sub_period = {
            "lord": sub_lord,
            "start": current_date.isoformat(),
            "end": end_date.isoformat(),
            "duration_years": round(sub_duration_years, 4),
        }

        if remaining_levels >= 2:
            sub_period["pratyantardasha"] = _compute_sub_periods(
                sub_lord, current_date, sub_duration_years, remaining_levels - 1
            )

        sub_periods.append(sub_period)
        current_date = end_date

    return sub_periods
