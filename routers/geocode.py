"""Geocode API router — /api/v1/geocode endpoint."""

from fastapi import APIRouter, HTTPException, Query

from services.geocode_service import geocode_place

router = APIRouter(prefix="/api/v1", tags=["geocode"])


@router.get("/geocode")
def geocode(place: str = Query(..., description="Place name to geocode")):
    """Geocode a place name to latitude, longitude, and timezone."""
    result = geocode_place(place)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Place not found: {place}")
    return result
