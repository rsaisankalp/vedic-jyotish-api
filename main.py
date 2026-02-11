"""FastAPI application entry point for the Vedic Jyotish Chart API."""

from fastapi import FastAPI

from routers import chart, geocode

app = FastAPI(
    title="Vedic Jyotish Chart API",
    description="Vedic astrology (Jyotish) birth chart calculation engine using Swiss Ephemeris.",
    version="1.0.0",
)

# Include routers
app.include_router(chart.router)
app.include_router(geocode.router)


@app.get("/health", tags=["system"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
