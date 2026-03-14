# Jacksonville ICW Fishing Report Analyzer

**Multi-spot, multi-factor fishing analysis for Jacksonville's Intracoastal Waterway.**

Fetches live data from 8 free APIs in parallel, scores 9 ICW spots and seasonal species, and generates a full report with pressure trends, solunar proximity, and a Go/No-Go verdict. Zero external dependencies — pure Python stdlib.

> **[See Example Output](EXAMPLE_OUTPUT.md)**

---

## Quick Start

```bash
git clone https://github.com/seang1121/Fishing-Report-Analyzer.git
cd Fishing-Report-Analyzer
python fishing_analyzer.py
```

No API keys required. No pip install needed. Report generates in <10 seconds.

### JSON Output

```bash
python fishing_analyzer.py --json
```

Pipe to Discord bots, dashboards, or anything that reads JSON.

---

## Data Sources (8 APIs, all free)

| Source | Endpoint | Data |
|--------|----------|------|
| NOAA CO-OPS | Station 8720218 | Tide predictions (Mayport) |
| NOAA CO-OPS | Station 8720267 | Tide predictions (St Johns Entrance) |
| NOAA CO-OPS | Station 8720218 | Wind, water temp, air temp, pressure (Mayport) |
| NOAA CO-OPS | Station 8720219 | Water temp (Dames Point, upriver) |
| NOAA CO-OPS | Station 8720218 (6hr) | Pressure trend (Rising/Falling/Steady) |
| Solunar API | api.solunar.org | Major/minor feeding windows, moon phase |
| Sunrise-Sunset | api.sunrise-sunset.org | Dawn/dusk/twilight times |
| NWS Forecast | api.weather.gov gridpoint | Wind/temp weather forecast (JAX) |

---

## 9 ICW Spots Ranked

| Spot | Wind Tolerance | Best Tide | Key Feature |
|------|---------------|-----------|-------------|
| Sisters Creek | 25 kts | Rising | Protected bends, oyster bars |
| Pablo Creek | 25 kts | Falling | Finger creek choke points |
| Nassau Sound / Ft George | 15 kts | Any | Tarpon summer, drum winter |
| Mayport Inlet / Jetties | 20 kts | Any | Deep water + jetty structure |
| St Johns Confluence | 20 kts | Rising | Salinity break, fish stack |
| Dutton Island Preserve | 25 kts | Falling | Sheltered flats, kayak-friendly |
| Guana River / GTM Reserve | 25 kts | Rising | Pristine sight-casting flats |
| Ft George Island Bridges | 20 kts | Any | Bridge pilings, current breaks |
| Amelia Island / Nassau River | 20 kts | Rising | Backwater creeks, less pressure |

---

## Report Sections

1. **Tides** — Hi/lo times + heights for 2 stations, rising/falling status
2. **Moon & Solunar** — Phase, illumination, major/minor feeding windows, proximity countdown
3. **Conditions** — Multi-station: water temp, air temp, wind, pressure + 6hr pressure trend
4. **Weather Forecast** — NWS forecast for today + tonight (JAX gridpoint)
5. **Species Outlook** — Season-aware scoring (temp + tide + pressure trend + solunar proximity + moon)
6. **All Spots Ranked** — All 9 spots scored with one-line reasoning
7. **Best Windows** — Dawn/dusk + solunar peaks + next tide transition
8. **Go/No-Go** — 100-point score with factor breakdown

---

## Go/No-Go (100 pts)

| Factor | Max Points |
|--------|-----------|
| Wind | 25 |
| Water Temp | 20 |
| Tide Movement | 15 |
| Pressure Trend | 15 |
| Solunar | 15 |
| Moon Phase | 10 |

75+: EXCELLENT | 55-74: GOOD | 35-54: FAIR | 0-34: POOR

---

## Configuration

Edit `config.json` to customize station IDs, products per station, and NWS gridpoint without touching Python code.

---

## Seasonal Knowledge

Species intelligence encoded from local charter captains (Catching Fire Charters), Florida Sportsman NE FL forecasts, CyberAngler ICW reports, Salt Strong, and FishingBooker Jacksonville guides.

---

## License

MIT License
