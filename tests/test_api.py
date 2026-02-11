"""Tests for API endpoints."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

SAMPLE_BIRTH = {
    "name": "Test Person",
    "date": "1990-05-15",
    "time": "14:30:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone_offset": 5.5,
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_full_chart():
    resp = client.post("/api/v1/chart", json=SAMPLE_BIRTH)
    assert resp.status_code == 200
    data = resp.json()

    # Check top-level keys
    assert "lagna" in data
    assert "grahas" in data
    assert "bhavas" in data
    assert "divisional_charts" in data
    assert "dasha" in data
    assert "panchanga" in data
    assert "ashtakavarga" in data

    # Lagna
    assert 1 <= data["lagna"]["rashi"] <= 12

    # 9 grahas
    assert len(data["grahas"]) == 9

    # 12 bhavas
    assert len(data["bhavas"]) == 12

    # 9 divisional charts
    assert len(data["divisional_charts"]) == 9

    # 9 mahadasha periods
    assert len(data["dasha"]) == 9

    # Panchanga components
    assert "tithi" in data["panchanga"]
    assert "karana" in data["panchanga"]
    assert "yoga" in data["panchanga"]
    assert "nakshatra" in data["panchanga"]
    assert "vara" in data["panchanga"]

    # Ashtakavarga — SAV total should be 337
    sav_total = data["ashtakavarga"]["sarvashtakavarga"]["total"]
    assert sav_total == 337, f"SAV total is {sav_total}, expected 337"


def test_divisional_endpoint():
    req = {**SAMPLE_BIRTH, "chart_type": "D9"}
    resp = client.post("/api/v1/chart/divisional", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["chart_type"] == "D9"
    assert len(data["grahas"]) == 9


def test_dasha_endpoint():
    req = {**SAMPLE_BIRTH, "levels": 2}
    resp = client.post("/api/v1/chart/dasha", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["dasha"]) == 9
    # Each mahadasha should have antardasha at level 2
    for d in data["dasha"]:
        assert "antardasha" in d


def test_invalid_date():
    bad = {**SAMPLE_BIRTH, "date": "not-a-date"}
    resp = client.post("/api/v1/chart", json=bad)
    assert resp.status_code == 422
