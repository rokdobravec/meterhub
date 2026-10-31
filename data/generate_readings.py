"""Generate sample 15-minute smart-meter readings for MeterHub.

Run:  python3 generate_readings.py   (writes the CSV files next to this script)
Seeded, so every run produces the same data.
"""
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).parent
random.seed(42)

START = datetime(2026, 1, 1, tzinfo=timezone.utc)   # first interval starts 00:00 UTC
DAYS = 59                                           # 1 Jan - 28 Feb 2026
STEP = timedelta(minutes=15)

# id, location, customer type, base load kWh/15min, daily-pattern scale, heating factor
METERS = [
    ("MTR-001", "Bled", "household", 0.08, 0.35, 0.00),
    ("MTR-002", "Kranj", "household", 0.10, 0.45, 0.00),
    ("MTR-003", "Radovljica", "small business", 0.30, 1.40, 0.00),
    ("MTR-004", "Jesenice", "household with heat pump", 0.12, 0.40, 0.55),
    ("MTR-005", "Lesce", "household with EV charger", 0.09, 0.40, 0.00),
]

def local_hour(ts_utc: datetime) -> float:
    # Jan-Feb: Slovenia is UTC+1 (no DST in this period)
    t = ts_utc + timedelta(hours=1)
    return t.hour + t.minute / 60

def household_shape(h: float) -> float:
    morning = math.exp(-((h - 7.5) ** 2) / 1.5)
    evening = math.exp(-((h - 19.5) ** 2) / 4.0)
    return 0.6 * morning + 1.0 * evening

def business_shape(h: float, weekday: int) -> float:
    if weekday >= 6:            # closed Sunday
        return 0.0
    open_h = 8 <= h < (13 if weekday == 5 else 19)
    return 1.0 if open_h else 0.0

def kwh(meter, ts_end: datetime) -> float:
    mid, loc, kind, base, scale, heat = meter
    h = local_hour(ts_end - STEP / 2)
    wd = (ts_end + timedelta(hours=1)).isoweekday()
    if kind == "small business":
        v = base + scale * business_shape(h, wd) * random.uniform(0.85, 1.1)
    else:
        v = base + scale * household_shape(h) * random.uniform(0.7, 1.3)
        if wd >= 6:
            v *= 1.15
    if heat:
        cold = 0.6 + 0.4 * math.cos((ts_end - START).days / DAYS * math.pi)  # colder in Jan
        v += heat * cold * (1.2 if h < 7 or h > 21 else 0.8) * random.uniform(0.8, 1.2)
    if kind.endswith("EV charger"):
        day = (ts_end - START).days
        if day % 3 == 0 and (h >= 22 or h < 1.5):
            v += 2.75          # 11 kW charger -> 2.75 kWh per 15 min
    v += random.gauss(0, 0.01)
    return round(max(v, 0.0), 3)

def iso(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")

rows = []
for m in METERS:
    ts = START + STEP
    end = START + timedelta(days=DAYS)
    while ts <= end:
        rows.append([m[0], iso(ts), f"{kwh(m, ts):.3f}"])
        ts += STEP

# Deliberate data-quality problems (documented in README):
by_meter = {}
for r in rows:
    by_meter.setdefault(r[0], []).append(r)

def remove(meter, start_iso, count):
    lst = by_meter[meter]
    i = next(k for k, r in enumerate(lst) if r[1] == start_iso)
    del lst[i:i + count]

remove("MTR-002", "2026-01-14T03:00:00Z", 1)    # single missing interval
remove("MTR-003", "2026-02-03T09:00:00Z", 8)    # 2-hour outage
remove("MTR-004", "2026-01-22T12:15:00Z", 3)    # 45-minute gap

def duplicate(meter, ts_iso, new_value=None):
    lst = by_meter[meter]
    i = next(k for k, r in enumerate(lst) if r[1] == ts_iso)
    dup = list(lst[i])
    if new_value is not None:
        dup[2] = new_value
    lst.insert(i + 1, dup)

duplicate("MTR-001", "2026-01-10T18:00:00Z")             # exact duplicate
duplicate("MTR-005", "2026-02-12T20:30:00Z", "0.999")    # conflicting duplicate

with open(OUT / "readings.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["meterId", "timestamp", "kwh"])
    for m in METERS:
        w.writerows(by_meter[m[0]])

with open(OUT / "meters.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["meterId", "location", "customerType"])
    for m in METERS:
        w.writerow([m[0], m[1], m[2]])

# Small file for parsing/validation exercises (week 2)
bad = [
    ["meterId", "timestamp", "kwh"],
    ["MTR-001", "2026-03-01T00:15:00Z", "0.112"],
    ["MTR-001", "2026-03-01T00:30:00Z", "0,118"],          # comma decimal separator
    ["MTR-001", "2026-03-01T00:45:00Z", ""],               # missing value
    ["MTR-001", "not-a-date", "0.120"],                    # bad timestamp
    ["MTR-001", "2026-03-01T01:15:00Z", "-0.050"],         # negative energy
    ["", "2026-03-01T01:30:00Z", "0.101"],                 # missing meter id
    ["MTR-001", "2026-03-01T01:45:00Z", "0.098", "extra"], # too many columns
    ["MTR-001", "2026-03-01T02:00:00Z", "0.095"],
]
with open(OUT / "readings_bad_lines.csv", "w", newline="") as f:
    csv.writer(f).writerows(bad)

# DST day: 29 Mar 2026, clocks go 02:00 -> 03:00 local, so the local day has 92 intervals
dst_start = datetime(2026, 3, 28, 23, 0, tzinfo=timezone.utc)   # 00:00 local (UTC+1)
dst_end = datetime(2026, 3, 29, 22, 0, tzinfo=timezone.utc)     # 24:00 local (UTC+2)
with open(OUT / "readings_dst_2026-03-29.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["meterId", "timestamp", "kwh"])
    ts = dst_start + STEP
    while ts <= dst_end:
        w.writerow(["MTR-001", iso(ts), f"{0.08 + random.uniform(0, 0.3):.3f}"])
        ts += STEP

print("done")
