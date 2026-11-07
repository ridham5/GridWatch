from datetime import date

import ieso

SAMPLE = """\\Hourly Demand Report,,,
\\Created at 2026-11-07 17:00:00,,,
\\For 2026,,,
Date,Hour,Market Demand,Ontario Demand
2026-11-05,1,15000,13000
2026-11-05,2,14500,12500
2026-11-05,18,19500,18000
2026-11-05,19,19800,18500
2026-11-06,1,15100,13100
2026-11-06,2,14600,12600
2026-11-06,18,19700,18200
2026-11-06,19,20000,18700
bad,row,here,
"""


def test_parse_skips_headers_and_bad_rows():
    rows = ieso.parse_demand_csv(SAMPLE)
    assert len(rows) == 8
    assert rows[0] == ieso.HourlyDemand(date(2026, 11, 5), 1, 13000)


def test_last_n_days_keeps_latest_dates():
    rows = ieso.last_n_days(ieso.parse_demand_csv(SAMPLE), 1)
    assert {r.day for r in rows} == {date(2026, 11, 6)}


def test_hourly_profile_averages_each_hour():
    profile = ieso.hourly_profile(ieso.parse_demand_csv(SAMPLE))
    assert profile[1] == 13050
    assert profile[19] == 18600


def test_forecast_flags_evening_peaks():
    result = ieso.forecast_peaks(ieso.parse_demand_csv(SAMPLE), days=7, top=2)
    assert result["peak_hours"] == [18, 19]
