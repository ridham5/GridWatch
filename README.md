# GridWatch: Ontario Electricity Demand Dashboard

![CI](https://github.com/ridham5/GridWatch/actions/workflows/ci.yml/badge.svg)

> **Note:** GridWatch was built by a team of 4 at **UofTHacks 13** (January 2026), where I was a
> backend developer. The original hackathon code is being moved over from the team repo. This
> version is a **rebuild of the same idea** and will be replaced with the original code once it
> is recovered.

GridWatch shows Ontario's real-time electricity demand from IESO public data and forecasts the
peak hours of the day, so households can shift laundry, dishwashers or EV charging to cheaper,
less strained hours.

## Features

- Pulls hourly Ontario demand (MW) from the IESO public demand report, cached for 15 minutes
- Forecasts peak hours by averaging each hour of the day over the last 7 days
- Dashboard with the latest demand, the expected peak hours, and an hourly demand chart

## Tech

Python · FastAPI · JavaScript · Chart.js · pytest · GitHub Actions

## API

| Endpoint | Returns |
| --- | --- |
| `GET /api/demand?days=2` | Hourly Ontario demand for the last N days |
| `GET /api/forecast?days=7&top=3` | Average demand by hour and the top peak hours |
| `GET /` | The dashboard |

## Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload      # open http://127.0.0.1:8000
pytest -v
```

Data source: [IESO public reports](https://reports.ieso.ca/public/Demand/).
