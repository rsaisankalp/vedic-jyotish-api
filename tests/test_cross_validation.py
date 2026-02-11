"""Comprehensive cross-validation tests against prokerala.com and deva.guru.

Each test case uses reference data fetched from prokerala.com (Lahiri ayanamsa)
and verified against deva.guru where applicable. All sign, degree (to arcminute),
and nakshatra/pada values have been cross-checked.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from main import app

from calculations.ephemeris import (
    datetime_to_jd, local_time_to_ut_hour, compute_all_planets,
    compute_houses, get_ayanamsa, compute_sunrise,
)
from calculations.grahas import compute_graha_positions
from calculations.panchanga import compute_panchanga
from calculations.dasha import compute_mahadasha
from calculations.divisional import (
    compute_divisional_chart, compute_all_divisional_charts,
    _d2_sign, _d3_sign, _d7_sign, _d9_sign, _d10_sign, _d12_sign, _d30_sign, _d60_sign,
)
from calculations.ashtakavarga import (
    compute_bhinnashtakavarga, compute_sarvashtakavarga,
)
from constants.rashis import longitude_to_rashi, RASHI_NAMES
from constants.nakshatras import longitude_to_nakshatra, longitude_to_pada

client = TestClient(app)


# ============================================================================
# REFERENCE DATA — verified against prokerala.com and deva.guru
# ============================================================================

# Format: (graha, sign_number, degree_int, minute_int)
# Sign numbers: 1=Mesha/Aries .. 12=Meena/Pisces

REFERENCE_CHARTS = {
    "sai_sankalp": {
        "birth": {
            "date": "1992-12-26", "time": "04:42:00",
            "latitude": 17.384, "longitude": 78.4564, "timezone_offset": 5.5,
        },
        "source": "deva.guru + prokerala.com",
        "lagna": (8, 12, 16),  # Vrischika 12°16'
        "grahas": {
            "Sun":     (9, 10, 40),   # Dhanu 10°40'
            "Moon":    (10, 2, 54),    # Makara 2°54'
            "Mars":    (3, 28, 53),    # Mithuna 28°53'
            "Mercury": (8, 24, 46),    # Vrischika 24°46'
            "Jupiter": (6, 19, 10),    # Kanya 19°10'
            "Venus":   (10, 26, 8),    # Makara 26°08'
            "Saturn":  (10, 21, 58),   # Makara 21°58'
            "Rahu":    (8, 26, 59),    # Vrischika 26°59'
            "Ketu":    (2, 26, 59),    # Vrishabha 26°59'
        },
        "panchanga": {
            "vara": "Friday",       # Sunrise-based (birth before sunrise)
            "tithi": "Dwitiya",
            "paksha": "Shukla",
            "yoga": "Vyaghata",
            "karana": "Kaulava",
            "nakshatra": "Uttara Ashadha",
        },
        "nakshatras": {
            "Sun":    (19, 4),  # Moola Pada 4
            "Moon":   (21, 2),  # Uttara Ashadha Pada 2
            "Mars":   (7, 3),   # Punarvasu Pada 3
            "Mercury": (18, 3), # Jyeshtha Pada 3
            "Jupiter": (13, 3), # Hasta Pada 3
            "Venus":  (23, 1),  # Dhanishtha Pada 1
            "Saturn": (22, 4),  # Shravana Pada 4
            "Rahu":   (18, 4),  # Jyeshtha Pada 4
            "Ketu":   (5, 2),   # Mrigashira Pada 2
        },
        "dignity": {"Saturn": "own_sign"},
    },

    "mumbai_1985": {
        "birth": {
            "date": "1985-03-21", "time": "06:15:00",
            "latitude": 19.076, "longitude": 72.8777, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (11, 26, 54),  # Kumbha 26°54'
        "grahas": {
            "Sun":     (12, 6, 42),
            "Moon":    (12, 1, 34),
            "Mars":    (1, 10, 34),
            "Mercury": (12, 24, 4),
            "Jupiter": (10, 15, 19),
            "Venus":   (12, 27, 33),
            "Saturn":  (8, 4, 19),
            "Rahu":    (1, 27, 18),
            "Ketu":    (7, 27, 18),
        },
        "panchanga": {
            "vara": "Wednesday",  # Birth at 6:15 before sunrise ~6:42
        },
    },

    "chennai_1975": {
        "birth": {
            "date": "1975-08-10", "time": "19:45:00",
            "latitude": 13.0827, "longitude": 80.2707, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (11, 15, 25),  # Kumbha 15°25'
        "grahas": {
            "Sun":     (4, 23, 49),
            "Moon":    (6, 7, 21),
            "Mars":    (2, 3, 48),
            "Mercury": (5, 3, 22),
            "Jupiter": (1, 1, 9),
            "Venus":   (5, 17, 49),
            "Saturn":  (4, 2, 18),
            "Rahu":    (8, 3, 20),
            "Ketu":    (2, 3, 20),
        },
        "panchanga": {
            "vara": "Sunday",  # Birth at 19:45, well after sunrise
        },
    },

    "delhi_2001": {
        "birth": {
            "date": "2001-01-15", "time": "01:30:00",
            "latitude": 28.6139, "longitude": 77.209, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (7, 12, 25),  # Tula 12°25'
        "grahas": {
            "Sun":     (10, 0, 51),
            "Moon":    (6, 9, 35),
            "Mars":    (7, 19, 4),
            "Mercury": (10, 13, 13),
            "Jupiter": (2, 7, 30),
            "Venus":   (11, 17, 55),
            "Saturn":  (2, 0, 17),
            "Rahu":    (3, 21, 4),
            "Ketu":    (9, 21, 4),
        },
        "panchanga": {
            "vara": "Sunday",  # Birth at 01:30 before sunrise ~07:14
        },
    },

    "kolkata_1968": {
        "birth": {
            "date": "1968-11-25", "time": "15:00:00",
            "latitude": 22.5726, "longitude": 88.3639, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (1, 9, 16),  # Mesha 9°16'
        "grahas": {
            "Sun":     (8, 9, 46),
            "Moon":    (10, 19, 50),
            "Mars":    (6, 16, 19),
            "Mercury": (8, 3, 11),
            "Jupiter": (6, 8, 4),
            "Venus":   (9, 19, 13),
            "Saturn":  (12, 25, 52),
            "Rahu":    (12, 13, 7),
            "Ketu":    (6, 13, 7),
        },
        "panchanga": {
            "vara": "Monday",  # Birth at 15:00, after sunrise
        },
    },

    "bangalore_1995": {
        "birth": {
            "date": "1995-07-04", "time": "04:20:00",
            "latitude": 12.9716, "longitude": 77.5946, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (2, 24, 24),  # Vrishabha 24°24'
        "grahas": {
            "Sun":     (3, 17, 44),
            "Moon":    (5, 24, 48),
            "Mars":    (5, 26, 12),
            "Mercury": (2, 26, 28),
            "Jupiter": (8, 13, 3),
            "Venus":   (3, 4, 35),
            "Saturn":  (12, 0, 57),
            "Rahu":    (7, 8, 13),
            "Ketu":    (1, 8, 13),
        },
        "panchanga": {
            "vara": "Monday",  # Birth at 04:20, before sunrise ~05:57
        },
    },

    "jaipur_2010": {
        "birth": {
            "date": "2010-12-01", "time": "23:55:00",
            "latitude": 26.9124, "longitude": 75.7873, "timezone_offset": 5.5,
        },
        "source": "prokerala.com",
        "lagna": (5, 11, 34),  # Simha 11°34'
        "grahas": {
            "Sun":     (8, 15, 26),
            "Moon":    (6, 23, 56),
            "Mars":    (9, 1, 18),
            "Mercury": (9, 6, 46),
            "Jupiter": (11, 29, 46),
            "Venus":   (7, 6, 44),
            "Saturn":  (6, 20, 37),
            "Rahu":    (9, 9, 53),
            "Ketu":    (3, 9, 53),
        },
        "panchanga": {
            "vara": "Wednesday",  # Birth at 23:55, after sunrise
        },
    },
}


# ============================================================================
# Helper functions
# ============================================================================

def _compute_jd(birth):
    y, m, d = map(int, birth["date"].split("-"))
    h, mi, s = map(int, birth["time"].split(":"))
    ut_hour = local_time_to_ut_hour(h, mi, s, birth["timezone_offset"])
    ud = d
    if ut_hour < 0:
        ut_hour += 24
        ud -= 1
    elif ut_hour >= 24:
        ut_hour -= 24
        ud += 1
    return datetime_to_jd(y, m, ud, ut_hour)


def _deg_min_to_float(deg, minute):
    return deg + minute / 60.0


# ============================================================================
# SIGN + DEGREE TESTS — verify against prokerala.com reference data
# ============================================================================

class TestSignPositions:
    """Verify graha signs match prokerala.com reference data for all 7 charts."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_all_graha_signs(self, chart_name):
        """All 9 graha signs must match reference data."""
        ref = REFERENCE_CHARTS[chart_name]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        for g in grahas:
            name = g["graha"]
            if name in ref["grahas"]:
                expected_sign = ref["grahas"][name][0]
                assert g["rashi"] == expected_sign, (
                    f"{chart_name}: {name} sign mismatch — "
                    f"got {g['rashi']} ({g['rashi_name']}), "
                    f"expected {expected_sign} ({RASHI_NAMES[expected_sign]})"
                )

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_lagna_sign(self, chart_name):
        """Lagna sign must match reference data."""
        ref = REFERENCE_CHARTS[chart_name]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        _, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])
        lagna_rashi = longitude_to_rashi(ascmc[0])
        expected_sign = ref["lagna"][0]
        assert lagna_rashi == expected_sign, (
            f"{chart_name}: Lagna sign mismatch — "
            f"got {lagna_rashi} ({RASHI_NAMES[lagna_rashi]}), "
            f"expected {expected_sign} ({RASHI_NAMES[expected_sign]})"
        )

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_graha_degrees_within_arcminute(self, chart_name):
        """All graha degrees must be within 2 arcminutes of reference data."""
        ref = REFERENCE_CHARTS[chart_name]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        for g in grahas:
            name = g["graha"]
            if name in ref["grahas"]:
                _, ref_deg, ref_min = ref["grahas"][name]
                ref_float = _deg_min_to_float(ref_deg, ref_min)
                diff = abs(g["degree_in_rashi"] - ref_float)
                # Allow up to 2 arcminutes (0.033°) tolerance
                assert diff < 0.034, (
                    f"{chart_name}: {name} degree mismatch — "
                    f"got {g['degree_in_rashi']:.4f}°, "
                    f"expected ~{ref_float:.2f}° (diff={diff:.4f}°)"
                )


# ============================================================================
# NAKSHATRA + PADA TESTS — verified against deva.guru
# ============================================================================

class TestNakshatraPada:
    """Verify nakshatra and pada for Sai Sankalp chart (verified against deva.guru)."""

    def test_sai_sankalp_nakshatras(self):
        ref = REFERENCE_CHARTS["sai_sankalp"]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        for g in grahas:
            name = g["graha"]
            if name in ref.get("nakshatras", {}):
                exp_nak, exp_pada = ref["nakshatras"][name]
                assert g["nakshatra"] == exp_nak, (
                    f"{name}: nakshatra mismatch — got {g['nakshatra']} "
                    f"({g['nakshatra_name']}), expected {exp_nak}"
                )
                assert g["pada"] == exp_pada, (
                    f"{name}: pada mismatch — got {g['pada']}, expected {exp_pada}"
                )

    def test_sai_sankalp_saturn_own_sign(self):
        """Saturn in Makara should be in own sign."""
        ref = REFERENCE_CHARTS["sai_sankalp"]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        saturn = next(g for g in grahas if g["graha"] == "Saturn")
        assert saturn["dignity"] == "own_sign"


# ============================================================================
# PANCHANGA TESTS — Vara (sunrise-based), Tithi, Yoga, Karana
# ============================================================================

class TestPanchanga:
    """Verify Panchanga elements, especially sunrise-based Vara."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_vara(self, chart_name):
        """Vara must use sunrise-to-sunrise convention."""
        ref = REFERENCE_CHARTS[chart_name]
        if "vara" not in ref.get("panchanga", {}):
            pytest.skip("No vara reference data")

        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)

        panchanga = compute_panchanga(
            positions["Sun"]["longitude"],
            positions["Moon"]["longitude"],
            jd, birth["timezone_offset"],
            birth["latitude"], birth["longitude"],
        )

        expected_vara = ref["panchanga"]["vara"]
        assert panchanga["vara"]["english"] == expected_vara, (
            f"{chart_name}: Vara mismatch — got {panchanga['vara']['english']}, "
            f"expected {expected_vara}"
        )

    def test_sai_sankalp_full_panchanga(self):
        """Full panchanga verification for Sai Sankalp against deva.guru."""
        ref = REFERENCE_CHARTS["sai_sankalp"]
        birth = ref["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)

        panchanga = compute_panchanga(
            positions["Sun"]["longitude"],
            positions["Moon"]["longitude"],
            jd, birth["timezone_offset"],
            birth["latitude"], birth["longitude"],
        )

        pk = ref["panchanga"]
        assert panchanga["vara"]["english"] == pk["vara"]
        assert panchanga["tithi"]["name"] == pk["tithi"]
        assert panchanga["tithi"]["paksha"] == pk["paksha"]
        assert panchanga["yoga"]["name"] == pk["yoga"]
        assert panchanga["karana"]["name"] == pk["karana"]
        assert pk["nakshatra"] in panchanga["nakshatra"]["name"]

    @pytest.mark.parametrize("chart_name,before_sunrise", [
        ("sai_sankalp", True),       # 04:42 AM, sunrise ~06:43
        ("mumbai_1985", True),       # 06:15 AM, sunrise ~06:42
        ("bangalore_1995", True),    # 04:20 AM, sunrise ~05:57
        ("delhi_2001", True),        # 01:30 AM, sunrise ~07:14
        ("chennai_1975", False),     # 19:45, well after sunrise
        ("kolkata_1968", False),     # 15:00, well after sunrise
        ("jaipur_2010", False),      # 23:55, well after sunrise
    ])
    def test_sunrise_detection(self, chart_name, before_sunrise):
        """Verify correct sunrise detection for vara calculation."""
        ref = REFERENCE_CHARTS[chart_name]
        birth = ref["birth"]
        jd = _compute_jd(birth)

        # Compute sunrise
        local_jd = jd + birth["timezone_offset"] / 24.0
        local_midnight_jd = int(local_jd + 0.5) - 0.5
        local_midnight_ut = local_midnight_jd - birth["timezone_offset"] / 24.0
        sunrise_jd = compute_sunrise(
            local_midnight_ut, birth["latitude"], birth["longitude"]
        )

        is_before = jd < sunrise_jd
        assert is_before == before_sunrise, (
            f"{chart_name}: sunrise detection wrong — "
            f"birth JD={jd:.6f}, sunrise JD={sunrise_jd:.6f}, "
            f"expected before_sunrise={before_sunrise}"
        )


# ============================================================================
# INVARIANT TESTS — mathematical properties that must always hold
# ============================================================================

class TestInvariants:
    """Mathematical invariants that must hold for any birth data."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_rahu_ketu_180_degrees(self, chart_name):
        """Rahu and Ketu must always be exactly 180° apart."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)

        rahu_lon = positions["Rahu"]["longitude"]
        ketu_lon = positions["Ketu"]["longitude"]
        diff = abs(rahu_lon - ketu_lon)
        assert abs(diff - 180.0) < 0.01, f"Rahu-Ketu diff={diff}°"

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_sarvashtakavarga_337(self, chart_name):
        """Sarvashtakavarga total must always equal 337."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        _, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])

        bav = compute_bhinnashtakavarga(positions, ascmc[0])
        sav = compute_sarvashtakavarga(bav)
        assert sum(sav) == 337, f"SAV total={sum(sav)}"

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_bav_planet_totals(self, chart_name):
        """Individual BAV planet totals must match BPHS values."""
        expected_totals = {
            "Sun": 48, "Moon": 49, "Mars": 39,
            "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39,
        }
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        _, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])

        bav = compute_bhinnashtakavarga(positions, ascmc[0])
        for planet, expected in expected_totals.items():
            actual = sum(bav[planet])
            assert actual == expected, (
                f"{chart_name}: {planet} BAV total={actual}, expected={expected}"
            )

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_all_longitudes_0_to_360(self, chart_name):
        """All planet longitudes must be in [0, 360) range."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)

        for name, pos in positions.items():
            assert 0 <= pos["longitude"] < 360, (
                f"{chart_name}: {name} longitude={pos['longitude']}"
            )

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_rashi_range(self, chart_name):
        """All rashis must be 1–12."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        for g in grahas:
            assert 1 <= g["rashi"] <= 12
            assert 1 <= g["nakshatra"] <= 27
            assert 1 <= g["pada"] <= 4
            assert 1 <= g["house"] <= 12

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_rahu_ketu_always_retrograde(self, chart_name):
        """Rahu and Ketu must always be marked retrograde."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        graha_dict = {g["graha"]: g for g in grahas}
        assert graha_dict["Rahu"]["retrograde"] is True
        assert graha_dict["Ketu"]["retrograde"] is True

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_twelve_houses(self, chart_name):
        """Must have exactly 12 house cusps."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        cusps, _ = compute_houses(jd, birth["latitude"], birth["longitude"])
        assert len(cusps) == 12


# ============================================================================
# DASHA TESTS — structure and duration invariants
# ============================================================================

class TestDasha:
    """Vimshottari Dasha structural tests."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_nine_mahadashas(self, chart_name):
        """Must have exactly 9 Mahadasha periods."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        y, m, d = map(int, birth["date"].split("-"))
        h, mi, s = map(int, birth["time"].split(":"))
        birth_dt = datetime(y, m, d, h, mi, s)

        dashas = compute_mahadasha(
            positions["Moon"]["longitude"], birth_dt, levels=1
        )
        assert len(dashas) == 9

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_dasha_total_under_120(self, chart_name):
        """Dasha total from birth must be <= 120 years."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        y, m, d = map(int, birth["date"].split("-"))
        h, mi, s = map(int, birth["time"].split(":"))
        birth_dt = datetime(y, m, d, h, mi, s)

        dashas = compute_mahadasha(
            positions["Moon"]["longitude"], birth_dt, levels=1
        )
        total = sum(d["duration_years"] for d in dashas)
        assert 100 < total <= 120.01

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_antardasha_sums_to_mahadasha(self, chart_name):
        """Each Mahadasha's Antardashas must sum to its duration."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        y, m, d = map(int, birth["date"].split("-"))
        h, mi, s = map(int, birth["time"].split(":"))
        birth_dt = datetime(y, m, d, h, mi, s)

        dashas = compute_mahadasha(
            positions["Moon"]["longitude"], birth_dt, levels=2
        )
        for d in dashas:
            antar_total = sum(a["duration_years"] for a in d["antardasha"])
            assert abs(antar_total - d["duration_years"]) < 0.05

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_dasha_periods_contiguous(self, chart_name):
        """Dasha periods must be contiguous (no gaps)."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        y, m, d = map(int, birth["date"].split("-"))
        h, mi, s = map(int, birth["time"].split(":"))
        birth_dt = datetime(y, m, d, h, mi, s)

        dashas = compute_mahadasha(
            positions["Moon"]["longitude"], birth_dt, levels=1
        )
        for i in range(len(dashas) - 1):
            assert dashas[i]["end"] == dashas[i + 1]["start"]


# ============================================================================
# DIVISIONAL CHART TESTS
# ============================================================================

class TestDivisional:
    """Divisional chart structural tests."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_nine_divisional_charts(self, chart_name):
        """Must compute all 9 divisional charts."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        _, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])

        charts = compute_all_divisional_charts(positions, ascmc[0])
        assert len(charts) == 9
        types = {c["chart_type"] for c in charts}
        assert types == {"D1", "D2", "D3", "D7", "D9", "D10", "D12", "D30", "D60"}

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_d1_matches_birth_chart(self, chart_name):
        """D1 chart signs must match the birth chart."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        cusps, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])
        grahas = compute_graha_positions(positions, cusps)

        d1 = compute_divisional_chart(positions, ascmc[0], "D1")
        for g in grahas:
            d1_graha = next(dg for dg in d1["grahas"] if dg["graha"] == g["graha"])
            assert d1_graha["rashi"] == g["rashi"], (
                f"{g['graha']}: D1 rashi={d1_graha['rashi']} != birth rashi={g['rashi']}"
            )

    @pytest.mark.parametrize("chart_type", ["D1", "D2", "D3", "D7", "D9", "D10", "D12", "D30", "D60"])
    def test_divisional_signs_in_range(self, chart_type):
        """All divisional chart signs must be 1-12."""
        birth = REFERENCE_CHARTS["sai_sankalp"]["birth"]
        jd = _compute_jd(birth)
        positions = compute_all_planets(jd)
        _, ascmc = compute_houses(jd, birth["latitude"], birth["longitude"])

        chart = compute_divisional_chart(positions, ascmc[0], chart_type)
        assert 1 <= chart["lagna"]["rashi"] <= 12
        for g in chart["grahas"]:
            assert 1 <= g["rashi"] <= 12

    def test_d9_against_deva_guru(self):
        """D9 Navamsa positions verified against deva.guru public chart.

        Chart: A, Dominique (1968-10-06 17:35, France [48.5589, 3.2994], CET +1).
        D1 positions from deva.guru graha table, D9 positions read from deva.guru
        North Indian D9 chart (house positions matched to signs).
        """
        # D1 longitudes from deva.guru (sign + degree -> absolute sidereal longitude)
        deva_d1_longitudes = {
            "Lagna":   331.14,   # Pi 1°8'
            "Sun":     170.08,   # Vi 20°5'
            "Moon":    352.40,   # Pi 22°24'
            "Mars":    135.93,   # Le 15°56'
            "Mercury": 187.22,   # Li 7°13'
            "Jupiter": 148.91,   # Le 28°55'
            "Venus":   198.85,   # Li 18°51'
            "Saturn":  359.37,   # Pi 29°22'
            "Rahu":    345.78,   # Pi 15°47'
            "Ketu":    165.78,   # Vi 15°47'
        }
        # D9 signs from deva.guru chart (North Indian format)
        deva_d9_signs = {
            "Lagna":   4,   # Cancer
            "Sun":     4,   # Cancer
            "Moon":    10,  # Capricorn
            "Mars":    5,   # Leo
            "Mercury": 9,   # Sagittarius
            "Jupiter": 9,   # Sagittarius
            "Venus":   12,  # Pisces
            "Saturn":  12,  # Pisces
            "Rahu":    8,   # Scorpio
            "Ketu":    2,   # Taurus
        }
        for name, lon in deva_d1_longitudes.items():
            our_d9 = _d9_sign(lon)
            expected = deva_d9_signs[name]
            assert our_d9 == expected, (
                f"D9 {name}: got {RASHI_NAMES[our_d9]}, "
                f"expected {RASHI_NAMES[expected]}"
            )

    def test_d9_absolute_pada_method(self):
        """D9 must agree with the absolute pada method (pada -> sign cycle)."""
        import random
        random.seed(42)
        for _ in range(200):
            lon = random.uniform(0, 360)
            # Method 1: Our element-based implementation
            our_d9 = _d9_sign(lon)
            # Method 2: Absolute pada (universally accepted)
            absolute_pada = int(lon / (360 / 108))
            expected = (absolute_pada % 12) + 1
            assert our_d9 == expected, (
                f"D9 mismatch at lon={lon:.4f}: "
                f"ours={RASHI_NAMES[our_d9]}, absolute_pada={RASHI_NAMES[expected]}"
            )

    def test_d9_textbook_boundary_values(self):
        """D9 boundary values from BPHS textbook rules."""
        # Fire signs start at Aries, Earth at Capricorn, Air at Libra, Water at Cancer
        cases = [
            # (longitude, expected_d9_sign, description)
            (0.1,    1,  "Aries 0° -> Aries"),
            (3.4,    2,  "Aries 3°20' -> Taurus"),
            (30.1,   10, "Taurus 0° -> Capricorn"),
            (60.1,   7,  "Gemini 0° -> Libra"),
            (90.1,   4,  "Cancer 0° -> Cancer"),
            (120.1,  1,  "Leo 0° -> Aries"),
            (150.1,  10, "Virgo 0° -> Capricorn"),
            (180.1,  7,  "Libra 0° -> Libra"),
            (210.1,  4,  "Scorpio 0° -> Cancer"),
            (240.1,  1,  "Sagittarius 0° -> Aries"),
            (270.1,  10, "Capricorn 0° -> Capricorn"),
            (300.1,  7,  "Aquarius 0° -> Libra"),
            (330.1,  4,  "Pisces 0° -> Cancer"),
        ]
        for lon, expected, desc in cases:
            result = _d9_sign(lon)
            assert result == expected, f"D9 {desc}: got {RASHI_NAMES[result]}, expected {RASHI_NAMES[expected]}"

    def test_d2_hora_textbook(self):
        """D2 Hora: odd signs -> Leo/Cancer, even signs -> Cancer/Leo."""
        assert _d2_sign(0.1) == 5    # Aries 0-15 -> Leo
        assert _d2_sign(20.0) == 4   # Aries 15-30 -> Cancer
        assert _d2_sign(30.1) == 4   # Taurus 0-15 -> Cancer
        assert _d2_sign(50.0) == 5   # Taurus 15-30 -> Leo

    def test_d3_drekkana_textbook(self):
        """D3 Drekkana: 3 parts -> same sign, 5th, 9th."""
        assert _d3_sign(5.0) == 1    # Aries 0-10 -> Aries (same)
        assert _d3_sign(15.0) == 5   # Aries 10-20 -> Leo (5th)
        assert _d3_sign(25.0) == 9   # Aries 20-30 -> Sagittarius (9th)
        assert _d3_sign(35.0) == 2   # Taurus 0-10 -> Taurus
        assert _d3_sign(45.0) == 6   # Taurus 10-20 -> Virgo (5th)
        assert _d3_sign(55.0) == 10  # Taurus 20-30 -> Capricorn (9th)

    def test_d10_dasamsa_textbook(self):
        """D10 Dasamsa: odd -> from same sign, even -> from 9th."""
        assert _d10_sign(0.1) == 1   # Aries (odd) part 0 -> Aries
        assert _d10_sign(3.1) == 2   # Aries part 1 -> Taurus
        assert _d10_sign(30.1) == 10 # Taurus (even) part 0 -> 9th from Taurus = Capricorn
        assert _d10_sign(33.1) == 11 # Taurus part 1 -> Aquarius

    def test_d12_dwadasamsa_textbook(self):
        """D12 Dwadasamsa: count from same sign."""
        assert _d12_sign(0.1) == 1   # Aries part 0 -> Aries
        assert _d12_sign(2.6) == 2   # Aries part 1 -> Taurus
        assert _d12_sign(30.1) == 2  # Taurus part 0 -> Taurus

    def test_d30_trimsamsa_textbook(self):
        """D30 Trimsamsa: unequal divisions per BPHS."""
        # Odd signs: Mars(0-5), Saturn(5-10), Jupiter(10-18), Mercury(18-25), Venus(25-30)
        assert _d30_sign(2.0) == 1    # Aries: Mars -> Aries
        assert _d30_sign(7.0) == 11   # Aries: Saturn -> Aquarius
        assert _d30_sign(14.0) == 9   # Aries: Jupiter -> Sagittarius
        assert _d30_sign(22.0) == 3   # Aries: Mercury -> Gemini
        assert _d30_sign(27.0) == 7   # Aries: Venus -> Libra
        # Even signs: Venus(0-5), Mercury(5-12), Jupiter(12-20), Saturn(20-25), Mars(25-30)
        assert _d30_sign(32.0) == 7   # Taurus: Venus -> Libra
        assert _d30_sign(39.0) == 3   # Taurus: Mercury -> Gemini
        assert _d30_sign(46.0) == 9   # Taurus: Jupiter -> Sagittarius
        assert _d30_sign(52.0) == 11  # Taurus: Saturn -> Aquarius
        assert _d30_sign(57.0) == 1   # Taurus: Mars -> Aries

    def test_d60_odd_even_symmetry(self):
        """D60 Shashtiamsa: odd signs forward, even signs backward."""
        # Odd sign (Aries): forward from Aries
        assert _d60_sign(0.1) == 1    # Aries part 0 -> Aries
        assert _d60_sign(0.6) == 2    # Aries part 1 -> Taurus
        # Even sign (Taurus): backward from Taurus
        assert _d60_sign(30.1) == 2   # Taurus part 0 -> Taurus
        assert _d60_sign(30.6) == 1   # Taurus part 1 -> Aries (backward)


# ============================================================================
# AYANAMSA TESTS
# ============================================================================

class TestAyanamsa:
    """Verify ayanamsa values are in expected ranges."""

    @pytest.mark.parametrize("year,expected_min,expected_max", [
        (1968, 23.35, 23.50),
        (1975, 23.45, 23.60),
        (1985, 23.58, 23.72),
        (1992, 23.69, 23.82),
        (1995, 23.72, 23.86),
        (2001, 23.80, 23.95),
        (2010, 23.94, 24.08),
    ])
    def test_ayanamsa_range(self, year, expected_min, expected_max):
        """Lahiri ayanamsa must be in expected range for each decade."""
        jd = datetime_to_jd(year, 6, 15, 12.0)
        ayanamsa = get_ayanamsa(jd)
        assert expected_min < ayanamsa < expected_max, (
            f"Year {year}: ayanamsa={ayanamsa:.4f}° not in "
            f"[{expected_min}, {expected_max}]"
        )


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestAPI:
    """API endpoint integration tests."""

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_chart_endpoint_returns_200(self, chart_name):
        """POST /api/v1/chart must return 200 for all test cases."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        resp = client.post("/api/v1/chart", json=birth)
        assert resp.status_code == 200

    @pytest.mark.parametrize("chart_name", REFERENCE_CHARTS.keys())
    def test_chart_response_completeness(self, chart_name):
        """Response must contain all required top-level keys."""
        birth = REFERENCE_CHARTS[chart_name]["birth"]
        resp = client.post("/api/v1/chart", json=birth)
        data = resp.json()

        required_keys = [
            "lagna", "grahas", "bhavas", "divisional_charts",
            "dasha", "panchanga", "ashtakavarga",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

        assert len(data["grahas"]) == 9
        assert len(data["bhavas"]) == 12
        assert len(data["divisional_charts"]) == 9
        assert len(data["dasha"]) == 9

    def test_api_graha_signs_match_prokerala(self):
        """API graha signs for Sai Sankalp must match prokerala reference."""
        birth = REFERENCE_CHARTS["sai_sankalp"]["birth"]
        resp = client.post("/api/v1/chart", json=birth)
        data = resp.json()

        ref = REFERENCE_CHARTS["sai_sankalp"]["grahas"]
        for g in data["grahas"]:
            name = g["graha"]
            if name in ref:
                assert g["rashi"] == ref[name][0], (
                    f"API {name}: rashi={g['rashi']}, expected={ref[name][0]}"
                )

    def test_divisional_endpoint(self):
        birth = REFERENCE_CHARTS["sai_sankalp"]["birth"]
        for chart_type in ["D1", "D9", "D10"]:
            req = {**birth, "chart_type": chart_type}
            resp = client.post("/api/v1/chart/divisional", json=req)
            assert resp.status_code == 200
            assert resp.json()["chart_type"] == chart_type

    def test_deva_guru_public_chart_full(self):
        """Full verification against deva.guru public chart: A, Dominique.

        Birth: 1968-10-06 17:35, France [48.5589, 3.2994], CET (UTC+1).
        All D1 signs, Panchanga elements, and Dasha lords verified against
        deva.guru public chart data.
        """
        resp = client.post("/api/v1/chart", json={
            "date": "1968-10-06", "time": "17:35:00",
            "latitude": 48.5589, "longitude": 3.2994,
            "timezone_offset": 1.0,
        })
        assert resp.status_code == 200
        data = resp.json()

        # D1 signs from deva.guru
        expected_signs = {
            "Sun": "Kanya", "Moon": "Meena", "Mars": "Simha",
            "Mercury": "Tula", "Jupiter": "Simha", "Venus": "Tula",
            "Saturn": "Meena", "Rahu": "Meena", "Ketu": "Kanya",
        }
        for g in data["grahas"]:
            if g["graha"] in expected_signs:
                assert g["rashi_name"] == expected_signs[g["graha"]], (
                    f"D1 {g['graha']}: got {g['rashi_name']}, "
                    f"expected {expected_signs[g['graha']]}"
                )
        assert data["lagna"]["rashi_name"] == "Meena"

        # Panchanga from deva.guru
        p = data["panchanga"]
        assert p["vara"]["english"] == "Sunday"
        assert p["tithi"]["name"] == "Pratipada"
        assert p["tithi"]["paksha"] == "Krishna"
        assert p["nakshatra"]["name"] == "Revati"
        assert p["karana"]["name"] == "Balava"
        assert p["yoga"]["name"] == "Vyaghata"

        # Dasha lord sequence from deva.guru (Moon in Revati -> Mercury first)
        expected_lords = ["Mercury", "Ketu", "Venus", "Sun", "Moon",
                          "Mars", "Rahu", "Jupiter", "Saturn"]
        for i, period in enumerate(data["dasha"]):
            assert period["lord"] == expected_lords[i], (
                f"Dasha {i}: got {period['lord']}, expected {expected_lords[i]}"
            )

    def test_dasha_endpoint_levels(self):
        birth = REFERENCE_CHARTS["sai_sankalp"]["birth"]
        for level in [1, 2, 3]:
            req = {**birth, "levels": level}
            resp = client.post("/api/v1/chart/dasha", json=req)
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["dasha"]) == 9

            if level >= 2:
                assert "antardasha" in data["dasha"][0]
            if level >= 3:
                assert "pratyantardasha" in data["dasha"][0]["antardasha"][0]
