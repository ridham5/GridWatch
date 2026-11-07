"""Fetch and analyze Ontario electricity demand from the IESO public reports.

Source: https://reports.ieso.ca/public/Demand/PUB_Demand.csv
Format: a few header lines starting with a backslash, then rows of
        Date,Hour,Market Demand,Ontario Demand   (Hour 1 = 00:00-01:00, values in MW)
"""

import csv
import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from urllib.request import urlopen

DEMAND_URL = "https://reports.ieso.ca/public/Demand/PUB_Demand.csv"


@dataclass
class HourlyDemand:
    day: date
    hour: int          # 1-24, as IESO reports it
    ontario_mw: int


def parse_demand_csv(text):
    """Turn the IESO CSV text into a list of HourlyDemand rows (skips header and comment lines)."""
    rows = []
    for record in csv.reader(io.StringIO(text)):
        if not record or record[0].startswith("\\") or record[0].strip().lower() == "date":
            continue
        try:
            day = date.fromisoformat(record[0].strip())
            hour = int(record[1])
            ontario = int(float(record[3]))
        except (ValueError, IndexError):
            continue
        rows.append(HourlyDemand(day, hour, ontario))
    return rows


def fetch_demand(url=DEMAND_URL, timeout=10):
    """Download the current year's demand report from IESO."""
    with urlopen(url, timeout=timeout) as response:
        return parse_demand_csv(response.read().decode("utf-8"))


def last_n_days(rows, days):
    """Keep only the rows from the most recent `days` dates."""
    recent = sorted({r.day for r in rows})[-days:]
    keep = set(recent)
    return [r for r in rows if r.day in keep]


def hourly_profile(rows):
    """Average Ontario demand for each hour of the day (1-24)."""
    totals, counts = defaultdict(int), defaultdict(int)
    for r in rows:
        totals[r.hour] += r.ontario_mw
        counts[r.hour] += 1
    return {h: round(totals[h] / counts[h]) for h in sorted(totals)}


def forecast_peaks(rows, days=7, top=3):
    """Simple forecast: average the last `days` days by hour and flag the `top` busiest hours.

    Households can shift laundry, dishwashers or EV charging away from these hours.
    """
    profile = hourly_profile(last_n_days(rows, days))
    peaks = sorted(profile, key=profile.get, reverse=True)[:top]
    return {"profile": profile, "peak_hours": sorted(peaks)}
