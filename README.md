# 🎣 Mayport Fishing Report Analyzer

**Comprehensive fishing report aggregator for Mayport, Jacksonville, FL**

Automatically pulls and consolidates fishing conditions from 6 professional data sources to give you the complete picture before heading out.

---

## 🌊 What Does This Do?

Generates a detailed fishing report by aggregating data from:

1. **ProAngler Jacksonville** - Recent fishing activity and catches
2. **FishingBooker Atlantic Beach** - Current conditions and species activity
3. **Tides4Fishing Atlantic Beach** - Solunar forecasts and tide predictions
4. **Tides4Fishing Mayport Bar Pilots Dock** ⭐ *PRIMARY SOURCE* - Detailed fishing ratings, weather, and tides
5. **NOAA Buoy MYPF1** - Live marine conditions (wind, water temp, air temp, pressure, gusts)
6. **TideTime Mayport** - Comprehensive tide predictions

### Sample Output

```
================================================================================
🎣 MAYPORT FISHING REPORT - Mayport, Jacksonville, FL
📍 30.3919° N, 81.4292° W
📅 Generated: 2026-02-15 09:30 AM
================================================================================

📰 PROANGLER JACKSONVILLE REPORT
--------------------------------------------------------------------------------
Inshore fishing has been excellent with redfish and trout active in the creeks...

🎯 FISHINGBOOKER CONDITIONS (Atlantic Beach)
--------------------------------------------------------------------------------
Water Temperature: 62°F | Clarity: Good | Wind: SE 10mph...

⭐ TIDES4FISHING - Mayport Bar Pilots Dock (PRIMARY)
--------------------------------------------------------------------------------
Fishing Rating: 82% (Very Good)
Weather: Partly Cloudy, 68°F, Wind SE 12mph
Tide Schedule:
High Tide: 06:45 AM (4.2 ft)
Low Tide: 12:30 PM (0.8 ft)...
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Internet connection

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/seang1121/Fishing-Report-Analyzer.git
   cd Fishing-Report-Analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analyzer:**
   ```bash
   python fishing_analyzer.py
   ```

That's it! The report will be printed to your terminal.

---

## 📋 Configuration

The `config.json` file contains all data sources and settings:

```json
{
  "location": {
    "name": "Mayport, Jacksonville, FL",
    "coordinates": "30.3919° N, 81.4292° W",
    "timezone": "EST"
  },
  "data_sources": {
    "proangler": "https://proangler.us/fishingreport/...",
    "fishingbooker": "https://fishingbooker.com/reports/...",
    ...
  }
}
```

**Want to change location?**
Simply update the URLs in `config.json` to point to your preferred fishing area.

---

## 🔧 How It Works

1. **Fetches Data**: Scrapes 6 fishing websites in sequence
2. **Parses Content**: Extracts relevant fishing conditions, tides, weather, and forecasts
3. **Consolidates**: Combines all data into a single comprehensive report
4. **Displays**: Outputs formatted report to terminal

### Respectful Scraping

- 1-second delay between requests
- Proper User-Agent headers
- 10-second timeout per request
- Graceful error handling

---

## 📊 Report Sections Explained

| Section | What It Tells You |
|---------|------------------|
| **ProAngler** | Recent catches, hot spots, species activity |
| **FishingBooker** | Current conditions (water temp, clarity, wind) |
| **Tides4Fishing Atlantic** | Solunar calendar (best fishing times) |
| **Tides4Fishing Mayport** | Overall fishing rating + detailed tides |
| **NOAA Buoy MYPF1** | Live marine data (wind speed/direction, water temp, air temp, pressure, gusts) |
| **TideTime** | Precise tide predictions for planning |

---

## 💡 Usage Tips

### Best Practices

- **Run before your trip** - Get the latest conditions
- **Check multiple times** - Conditions change throughout the day
- **Compare sources** - If sources disagree, weather may be changing rapidly
- **Focus on Tides4Fishing Mayport** - This is the most comprehensive source

### Example Use Cases

1. **Pre-Trip Planning**: Run the night before to plan your departure time
2. **Quick Check**: Run in the morning to confirm conditions haven't changed
3. **Tide Timing**: Use tide predictions to plan fishing around high/low tides

---

## 🛠️ Customization

### Change Location

Edit `config.json` to point to different fishing areas:

```json
{
  "location": {
    "name": "Your Location",
    "coordinates": "XX.XXXX° N, XX.XXXX° W"
  },
  "data_sources": {
    "tides4fishing_mayport": "https://tides4fishing.com/us/.../your-location"
  }
}
```

### Add New Sources

Extend the `FishingReportAnalyzer` class with new methods:

```python
def get_new_source(self):
    soup = self.fetch_url(self.sources['new_source'])
    # Your parsing logic here
    return data
```

---

## 🐛 Troubleshooting

### "Unable to fetch [source]"

- **Check internet connection**
- **Website may be temporarily down** - Try again in a few minutes
- **URL may have changed** - Update `config.json` with new URL

### "Error parsing [source]"

- **Website structure changed** - May need to update parsing logic
- **Network timeout** - Try running again

### Dependencies Not Found

```bash
pip install --upgrade requests beautifulsoup4 lxml
```

---

## 📜 License

MIT License - Feel free to use, modify, and distribute

---

## 🙏 Acknowledgments

Data sources:
- ProAngler US
- FishingBooker
- Tides4Fishing
- NOAA Tides & Currents
- TideTime

---

## 📞 Questions?

**Want to contribute?**
Open an issue or pull request on GitHub

**Found a bug?**
Report it in the Issues tab

---

**Built for anglers who want comprehensive data before heading out to Mayport, Jacksonville, FL**

*Last updated: February 2026*
