"""GridWatch API.

Run:  pip install -r requirements.txt
      uvicorn app:app --reload        # http://127.0.0.1:8000/docs
"""

import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import ieso

app = FastAPI(title="GridWatch")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

CACHE_SECONDS = 15 * 60  # IESO updates hourly; avoid re-downloading on every request
_cache = {"rows": None, "at": 0.0}
FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"


def demand_rows():
    if _cache["rows"] is None or time.time() - _cache["at"] > CACHE_SECONDS:
        try:
            _cache["rows"] = ieso.fetch_demand()
            _cache["at"] = time.time()
        except OSError as err:
            if _cache["rows"] is None:
                raise HTTPException(503, f"Could not reach IESO: {err}") from err
    return _cache["rows"]


@app.get("/api/demand")
def demand(days: int = Query(2, ge=1, le=31)):
    """Hourly Ontario demand (MW) for the last `days` days."""
    rows = ieso.last_n_days(demand_rows(), days)
    return [{"date": r.day.isoformat(), "hour": r.hour, "ontario_mw": r.ontario_mw} for r in rows]


@app.get("/api/forecast")
def forecast(days: int = Query(7, ge=1, le=31), top: int = Query(3, ge=1, le=6)):
    """Average demand by hour over the last `days` days, plus the expected peak hours."""
    return ieso.forecast_peaks(demand_rows(), days=days, top=top)


@app.get("/")
def dashboard():
    return FileResponse(FRONTEND)
