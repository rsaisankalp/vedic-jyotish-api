"""Pydantic request models."""

from pydantic import BaseModel, Field
from typing import Optional


class BirthDataRequest(BaseModel):
    """Birth details for chart calculation."""

    name: Optional[str] = Field(None, description="Person's name")
    date: str = Field(..., description="Birth date in YYYY-MM-DD format",
                      pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., description="Birth time in HH:MM:SS format",
                      pattern=r"^\d{2}:\d{2}:\d{2}$")
    latitude: float = Field(..., ge=-90, le=90, description="Birth latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth longitude")
    timezone_offset: float = Field(
        ..., ge=-12, le=14,
        description="Timezone offset from UTC in hours (e.g. 5.5 for IST)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Example Person",
                    "date": "1990-05-15",
                    "time": "14:30:00",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone_offset": 5.5,
                }
            ]
        }
    }


class DivisionalChartRequest(BirthDataRequest):
    """Request for a specific divisional chart."""

    chart_type: str = Field(
        "D9", description="Divisional chart type (D1, D2, D3, D7, D9, D10, D12, D30, D60)"
    )


class DashaRequest(BirthDataRequest):
    """Request for Vimshottari Dasha calculation."""

    levels: int = Field(
        3, ge=1, le=3,
        description="Depth of sub-periods (1=Maha, 2=+Antar, 3=+Pratyantar)"
    )
