"""Pydantic response models."""

from pydantic import BaseModel
from typing import Optional


class LagnaResponse(BaseModel):
    longitude: float
    rashi: int
    rashi_name: str
    degree_in_rashi: float
    nakshatra: int
    nakshatra_name: str
    pada: int


class GrahaPosition(BaseModel):
    graha: str
    graha_sanskrit: str
    longitude: float
    rashi: int
    rashi_name: str
    rashi_lord: str
    degree_in_rashi: float
    nakshatra: int
    nakshatra_name: str
    nakshatra_lord: str
    pada: int
    house: int
    retrograde: bool
    speed: float
    dignity: Optional[str] = None


class BhavaResponse(BaseModel):
    house: int
    cusp_longitude: float
    rashi: int
    rashi_name: str
    lord: str


class DivisionalGraha(BaseModel):
    graha: str
    rashi: int
    rashi_name: str


class DivisionalLagna(BaseModel):
    rashi: int
    rashi_name: str


class DivisionalChartResponse(BaseModel):
    chart_type: str
    lagna: DivisionalLagna
    grahas: list[DivisionalGraha]


class DashaPeriod(BaseModel):
    lord: str
    start: str
    end: str
    duration_years: float
    antardasha: Optional[list["DashaPeriod"]] = None
    pratyantardasha: Optional[list["DashaPeriod"]] = None


class TithiResponse(BaseModel):
    number: int
    name: str
    paksha: str


class KaranaResponse(BaseModel):
    number: int
    name: str


class YogaResponse(BaseModel):
    number: int
    name: str


class NakshatraResponse(BaseModel):
    number: int
    name: str
    lord: str
    pada: int


class VaraResponse(BaseModel):
    name: str
    english: str


class PanchangaResponse(BaseModel):
    tithi: TithiResponse
    karana: KaranaResponse
    yoga: YogaResponse
    nakshatra: NakshatraResponse
    vara: VaraResponse


class BAVDetail(BaseModel):
    bindus: list[int]
    total: int
    by_rashi: dict[str, int]


class SAVDetail(BaseModel):
    bindus: list[int]
    total: int
    by_rashi: dict[str, int]


class AshtakavargaResponse(BaseModel):
    bhinnashtakavarga: dict[str, BAVDetail]
    sarvashtakavarga: SAVDetail


class ChartResponse(BaseModel):
    name: Optional[str] = None
    birth_data: dict
    ayanamsa: float
    lagna: LagnaResponse
    grahas: list[GrahaPosition]
    bhavas: list[BhavaResponse]
    divisional_charts: list[DivisionalChartResponse]
    dasha: list[DashaPeriod]
    panchanga: PanchangaResponse
    ashtakavarga: AshtakavargaResponse


class GeocodeResponse(BaseModel):
    place: str
    latitude: float
    longitude: float
    timezone: str
    timezone_offset: float
