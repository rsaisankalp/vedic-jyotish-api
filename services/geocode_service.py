"""Geocode service — place name to lat/lng/timezone."""
from __future__ import annotations

from datetime import datetime

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

import pytz


_geolocator = Nominatim(user_agent="vedic-jyotish-api")
_tf = TimezoneFinder()


def geocode_place(place: str) -> dict | None:
    """Geocode a place name to latitude, longitude, and timezone.

    Args:
        place: Place name string (e.g. "New Delhi, India").

    Returns:
        Dict with place, latitude, longitude, timezone, timezone_offset,
        or None if not found.
    """
    location = _geolocator.geocode(place)
    if location is None:
        return None

    lat = location.latitude
    lng = location.longitude

    tz_name = _tf.timezone_at(lat=lat, lng=lng)
    if tz_name is None:
        tz_name = "UTC"

    # Compute current UTC offset for the timezone
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    offset_seconds = now.utcoffset().total_seconds()
    offset_hours = offset_seconds / 3600

    return {
        "place": location.address,
        "latitude": round(lat, 6),
        "longitude": round(lng, 6),
        "timezone": tz_name,
        "timezone_offset": offset_hours,
    }
