"""Chart API router — /api/v1/chart endpoints."""

from fastapi import APIRouter, HTTPException

from models.request import BirthDataRequest, DivisionalChartRequest, DashaRequest
from services.chart_service import (
    compute_full_chart, compute_single_divisional, compute_dasha_only,
)

router = APIRouter(prefix="/api/v1/chart", tags=["chart"])


@router.post("")
def get_full_chart(req: BirthDataRequest):
    """Compute a full Vedic birth chart with all components."""
    try:
        result = compute_full_chart(
            name=req.name,
            date_str=req.date,
            time_str=req.time,
            latitude=req.latitude,
            longitude=req.longitude,
            tz_offset=req.timezone_offset,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/divisional")
def get_divisional_chart(req: DivisionalChartRequest):
    """Compute a single divisional chart (D1–D60)."""
    try:
        result = compute_single_divisional(
            date_str=req.date,
            time_str=req.time,
            latitude=req.latitude,
            longitude=req.longitude,
            tz_offset=req.timezone_offset,
            chart_type=req.chart_type,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dasha")
def get_dasha(req: DashaRequest):
    """Compute Vimshottari Dasha periods (1–3 levels deep)."""
    try:
        result = compute_dasha_only(
            date_str=req.date,
            time_str=req.time,
            latitude=req.latitude,
            longitude=req.longitude,
            tz_offset=req.timezone_offset,
            levels=req.levels,
        )
        return {"dasha": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
