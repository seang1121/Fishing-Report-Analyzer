# Jacksonville ICW Fishing Report Analyzer

**Multi-spot, multi-factor fishing intelligence for Jacksonville's Intracoastal Waterway.**

[![Status: Active](https://img.shields.io/badge/status-active-green.svg)]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-blue.svg)]()

---

## What It Does

Fetches live data from 8 free APIs in parallel, scores 9 ICW fishing spots and 10 seasonal species, and generates a comprehensive report with pressure trends, solunar proximity, and a 100-point Go/No-Go verdict. Zero external dependencies -- pure Python stdlib using `urllib`, `json`, and `concurrent.futures`.

---

## Features

- **8 Parallel API Calls** -- NOAA CO-OPS tides, wind, water temp, air temp, pressure; Solunar feeding windows; Sunrise-Sunset times; NWS weather forecast
- **9 ICW Spot Rankings** -- Each spot scored by wind tolerance, optimal tide, and structure type
- **10 Species Scoring** -- Season-aware species outlook factoring water temp, tide direction, pressure trend, solunar proximity, and moon phase
- **100-Point Go/No-Go Verdict** -- Wind (25), water temp (20), tide movement (15), pressure trend (15), solunar (15), moon phase (10)
- **Pressure Trend Analysis** -- 6-hour barometric pressure trend (rising/falling/steady)
- **Solunar Proximity Countdown** -- Minutes to next major/minor feeding window
- **Best Windows** -- Dawn/dusk + solunar peaks + next tide transition
- **JSON Output Mode** -- Pipe to Discord bots, dashboards, or downstream tools
- **Configurable Stations** -- Edit `config.json` to customize NOAA stations and NWS gridpoint

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ (stdlib only) |
| HTTP | `urllib.request` |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Data Sources | NOAA CO-OPS, NWS, Solunar API, Sunrise-Sunset API |

---

## Quick Start

```bash
git clone https://github.com/seang1121/Fishing-Report-Analyzer.git
cd Fishing-Report-Analyzer
python fishing_analyzer.py
```

No API keys required. No `pip install` needed. Report generates in under 10 seconds.

### JSON Output

```bash
python fishing_analyzer.py --json
```

---

## Data Sources (8 APIs, all free)

| Source | Data |
|--------|------|
| NOAA CO-OPS (Mayport) | Tide predictions, wind, water temp, air temp, pressure |
| NOAA CO-OPS (St Johns Entrance) | Tide predictions |
| NOAA CO-OPS (Dames Point) | Upriver water temp |
| NOAA CO-OPS (6hr history) | Barometric pressure trend |
| Solunar API | Major/minor feeding windows, moon phase |
| Sunrise-Sunset API | Dawn, dusk, twilight times |
| NWS Forecast | Wind and temperature forecast |

---

## 9 ICW Spots

| Spot | Wind Tolerance | Best Tide |
|------|---------------|-----------|
| Sisters Creek | 25 kts | Rising |
| Pablo Creek | 25 kts | Falling |
| Nassau Sound / Ft George | 15 kts | Any |
| Mayport Inlet / Jetties | 20 kts | Any |
| St Johns Confluence | 20 kts | Rising |
| Dutton Island Preserve | 25 kts | Falling |
| Guana River / GTM Reserve | 25 kts | Rising |
| Ft George Island Bridges | 20 kts | Any |
| Amelia Island / Nassau River | 20 kts | Rising |

---

## Go/No-Go Scoring (100 pts)

| Factor | Max Points |
|--------|-----------|
| Wind | 25 |
| Water Temp | 20 |
| Tide Movement | 15 |
| Pressure Trend | 15 |
| Solunar | 15 |
| Moon Phase | 10 |

**75+**: EXCELLENT | **55-74**: GOOD | **35-54**: FAIR | **0-34**: POOR

> **[See Example Output](EXAMPLE_OUTPUT.md)**

---

## License

MIT License
