# Fishing Report Analyzer

**Aggregates fishing conditions from 6 data sources for Mayport, Jacksonville FL.**

Scrapes real-time data from ProAngler, FishingBooker, Tides4Fishing, NOAA, and TideTime — consolidates everything into one report so you know what's biting before you head out.

## Quick Start

```bash
git clone https://github.com/seang1121/Fishing-Report-Analyzer.git
cd Fishing-Report-Analyzer
pip install -r requirements.txt
python fishing_analyzer.py
```

## Data Sources

| Source | Data |
|--------|------|
| ProAngler Jacksonville | Recent catches, species activity, hot spots |
| FishingBooker Atlantic Beach | Water temp, clarity, wind, species |
| Tides4Fishing Atlantic Beach | Solunar forecast, best fishing windows |
| **Tides4Fishing Mayport** (primary) | Fishing rating, weather, full tide schedule |
| NOAA Buoy MYPF1 | Live wind, water temp, air temp, pressure, gusts |
| TideTime Mayport | Tide predictions |

## Example Output

```
================================================================================
MAYPORT FISHING REPORT - Mayport, Jacksonville, FL
30.3919 N, 81.4292 W
Generated: 2026-03-14 06:15 AM
================================================================================

PROANGLER JACKSONVILLE
--------------------------------------------------------------------------------
Inshore fishing strong — redfish and trout active in the creeks around Mayport.
Water temps low 60s, fish responding to live shrimp and soft plastics.
Best action on incoming tides early morning.

TIDES4FISHING - Mayport Bar Pilots Dock (PRIMARY)
--------------------------------------------------------------------------------
Fishing Rating: 82% (Very Good)
Weather: Partly Cloudy, 68F, Wind SE 12mph, Humidity 65%
High Tide: 06:45 AM (4.2 ft)
Low Tide: 12:30 PM (0.8 ft)
High Tide: 07:15 PM (4.5 ft)

NOAA BUOY MYPF1
--------------------------------------------------------------------------------
Wind Direction: SSE (150)
Wind Speed: 5.1 knots
Wind Gust: 9.9 knots
Pressure: 30.09 in
Air Temp: 61.9F
Water Temp: 56.5F

================================================================================
Report complete.
================================================================================
```

## Configuration

Edit `config.json` to change location or data source URLs:

```json
{
  "location": {
    "name": "Mayport, Jacksonville, FL",
    "coordinates": "30.3919 N, 81.4292 W"
  },
  "data_sources": {
    "proangler": "https://proangler.us/fishingreport/jacksonville-fishing-report/",
    "tides4fishing_mayport": "https://tides4fishing.com/us/florida-east-coast/mayport-bar-pilots-dock",
    "noaa_buoy": "https://www.ndbc.noaa.gov/station_page.php?station=mypf1"
  }
}
```

## Requirements

- Python 3.7+
- `requests`, `beautifulsoup4`, `lxml`

## License

MIT
