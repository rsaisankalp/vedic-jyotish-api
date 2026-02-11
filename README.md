# Vedic Jyotish Chart API

A complete Vedic astrology (Jyotish) birth chart calculation engine exposed as a REST API. Built with the Swiss Ephemeris for astronomical precision, cross-validated against [prokerala.com](https://www.prokerala.com/astrology/birth-chart/) and [deva.guru](https://deva.guru/).

## What It Calculates

| Feature | Details |
|---------|---------|
| **Lagna (Ascendant)** | Sidereal, Lahiri/Chitrapaksha ayanamsa |
| **9 Grahas** | Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu |
| **12 Bhavas** | Equal house system |
| **9 Divisional Charts** | D1, D2, D3, D7, D9, D10, D12, D30, D60 |
| **Vimshottari Dasha** | Mahadasha, Antardasha, Pratyantardasha (3 levels) |
| **Panchanga** | Tithi, Karana, Yoga, Nakshatra, Vara (sunrise-based) |
| **Ashtakavarga** | Bhinnashtakavarga + Sarvashtakavarga |

Each graha includes: sidereal longitude, rashi (1-12), nakshatra (1-27), pada (1-4), house placement, retrograde status, and dignity (exalted/debilitated/own sign).

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` for the interactive Swagger UI.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/chart` | Full birth chart |
| `POST` | `/api/v1/chart/divisional` | Single divisional chart (D1-D60) |
| `POST` | `/api/v1/chart/dasha` | Vimshottari dasha periods |
| `GET` | `/api/v1/geocode?place=...` | Geocode place name to lat/lng/timezone |
| `GET` | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/chart \
  -H "Content-Type: application/json" \
  -d '{
    "date": "1992-12-26",
    "time": "04:42:00",
    "latitude": 17.385,
    "longitude": 78.4867,
    "timezone_offset": 5.5
  }'
```

## Technical Details

- **Ayanamsa**: Lahiri (Chitrapaksha) via `swe.SIDM_LAHIRI`
- **Nodes**: Mean node (`swe.MEAN_NODE`) for Rahu; Ketu = Rahu + 180
- **Ephemeris**: Built-in Moshier (arc-second precision, no external files needed)
- **Sidereal**: `FLG_SIDEREAL | FLG_SPEED` on all calculations
- **Vara**: Sunrise-to-sunrise convention (Jyotish standard)
- **Dasha**: 365.25 days/year for period calculations

## Cross-Validation

All calculations are verified against external references:

- **8 reference charts** verified against prokerala.com (sign, degree to arcminute, nakshatra, pada)
- **D9 Navamsa** verified against deva.guru public chart (10/10 positions match)
- **Panchanga** verified against deva.guru (Vara, Tithi, Paksha, Nakshatra, Karana, Yoga)
- **Dasha lord sequence** verified against deva.guru
- **197 automated tests** covering positions, invariants, divisional charts, dasha structure, and API endpoints

## Running Tests

```bash
pip install pytest pytest-asyncio httpx
python -m pytest tests/ -v
```

## Project Structure

```
chartApi/
├── main.py                     # FastAPI app
├── config.py                   # Ayanamsa, house system defaults
├── constants/                  # Lookup tables (rashis, nakshatras, dashas, etc.)
├── calculations/               # Core computation modules
│   ├── ephemeris.py            # Swiss Ephemeris wrapper
│   ├── lagna.py                # Ascendant
│   ├── bhavas.py               # House cusps
│   ├── grahas.py               # 9 graha positions
│   ├── divisional.py           # D1-D60 algorithms
│   ├── dasha.py                # Vimshottari dasha
│   ├── panchanga.py            # Tithi, Karana, Yoga, Nakshatra, Vara
│   └── ashtakavarga.py         # BAV + SAV
├── models/                     # Pydantic request/response schemas
├── services/                   # Chart orchestrator + geocoding
├── routers/                    # API endpoints
└── tests/                      # 197 tests including cross-validation
```

## License

MIT
