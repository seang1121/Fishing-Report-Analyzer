#!/usr/bin/env python3
"""
Mayport Fishing Report Analyzer
Aggregates fishing conditions from 6 sources for Mayport, Jacksonville, FL
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import sys

class FishingReportAnalyzer:
    def __init__(self, config_file="config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.sources = self.config['data_sources']
        self.location = self.config['location']

    def fetch_url(self, url, delay=1):
        """Fetch URL with user agent and delay"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        try:
            time.sleep(delay)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"⚠️  Error fetching {url}: {str(e)}")
            return None

    def get_proangler_report(self):
        """Source 1: ProAngler Jacksonville Report"""
        soup = self.fetch_url(self.sources['proangler'])
        if not soup:
            return "Unable to fetch ProAngler report"

        try:
            # Extract recent fishing report content
            report_section = soup.find('div', class_='entry-content')
            if report_section:
                paragraphs = report_section.find_all('p')[:3]
                return '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            return "No recent report found"
        except:
            return "Error parsing ProAngler report"

    def get_fishingbooker_report(self):
        """Source 2: FishingBooker Atlantic Beach"""
        soup = self.fetch_url(self.sources['fishingbooker'])
        if not soup:
            return "Unable to fetch FishingBooker report"

        try:
            # Extract conditions and species info
            conditions = soup.find('div', class_='conditions')
            if conditions:
                return conditions.get_text().strip()
            return "No conditions data found"
        except:
            return "Error parsing FishingBooker report"

    def get_tides4fishing_atlantic(self):
        """Source 3: Tides4Fishing Atlantic Beach"""
        soup = self.fetch_url(self.sources['tides4fishing_atlantic'])
        if not soup:
            return "Unable to fetch Tides4Fishing Atlantic Beach"

        try:
            # Extract solunar forecast and tide times
            forecast = soup.find('div', class_='solunar_forecast')
            tides = soup.find('table', class_='tabla_mareas')

            result = []
            if forecast:
                result.append(f"Solunar Forecast: {forecast.get_text().strip()[:200]}")
            if tides:
                result.append(f"Tide Times: {tides.get_text().strip()[:200]}")

            return '\n'.join(result) if result else "No forecast data found"
        except:
            return "Error parsing Tides4Fishing Atlantic Beach"

    def get_tides4fishing_mayport(self):
        """Source 4: Tides4Fishing Mayport Bar Pilots Dock (PRIMARY)"""
        soup = self.fetch_url(self.sources['tides4fishing_mayport'])
        if not soup:
            return "Unable to fetch Tides4Fishing Mayport"

        try:
            # This is the primary source - get detailed info
            fishing_rating = soup.find('div', class_='nota_pesca')
            weather = soup.find('div', class_='tiempo')
            tides = soup.find('table', class_='tabla_mareas')

            result = []
            if fishing_rating:
                result.append(f"Fishing Rating: {fishing_rating.get_text().strip()}")
            if weather:
                result.append(f"Weather: {weather.get_text().strip()[:150]}")
            if tides:
                tide_data = tides.get_text().strip()[:300]
                result.append(f"Tide Schedule:\n{tide_data}")

            return '\n'.join(result) if result else "No detailed data found"
        except:
            return "Error parsing Tides4Fishing Mayport"

    def get_noaa_conditions(self):
        """Source 5: NOAA Buoy Station MYPF1 (Mayport Bar Pilots Dock)"""
        soup = self.fetch_url(self.sources['noaa_buoy'])
        if not soup:
            return "Unable to fetch NOAA buoy data"

        try:
            # Extract buoy measurements from the data table
            result = []

            # Find the meteorological data table
            data_rows = soup.find_all('tr')

            measurements = {}
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()

                    # Collect key measurements
                    if 'Wind Direction' in label or 'WDIR' in label:
                        measurements['Wind Direction'] = value
                    elif 'Wind Speed' in label and 'WSPD' in label and '10M' not in label and '20M' not in label:
                        measurements['Wind Speed'] = value
                    elif 'Wind Gust' in label or 'GST' in label:
                        measurements['Wind Gust'] = value
                    elif 'Atmospheric Pressure' in label or 'PRES' in label:
                        measurements['Pressure'] = value
                    elif 'Air Temperature' in label or 'ATMP' in label:
                        measurements['Air Temp'] = value
                    elif 'Water Temperature' in label or 'WTMP' in label:
                        measurements['Water Temp'] = value

            # Format the output
            if measurements:
                result.append("🌡️ Current Buoy Readings (MYPF1):")
                for key, value in measurements.items():
                    result.append(f"  • {key}: {value}")
                return '\n'.join(result)
            else:
                return "Buoy data table found but no measurements extracted"

        except Exception as e:
            return f"Error parsing NOAA buoy data: {str(e)}"

    def get_tidetime_info(self):
        """Source 6: TideTime"""
        soup = self.fetch_url(self.sources['tidetime'])
        if not soup:
            return "Unable to fetch TideTime data"

        try:
            # Extract tide predictions
            tide_table = soup.find('table', class_='tide-table')
            if tide_table:
                rows = tide_table.find_all('tr')[:5]
                return '\n'.join([row.get_text().strip() for row in rows])
            return "No tide predictions found"
        except:
            return "Error parsing TideTime data"

    def generate_report(self):
        """Generate comprehensive fishing report"""
        print(f"\n{'='*80}")
        print(f"🎣 MAYPORT FISHING REPORT - {self.location['name']}")
        print(f"📍 {self.location['coordinates']}")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"{'='*80}\n")

        # Source 1: ProAngler
        print("📰 PROANGLER JACKSONVILLE REPORT")
        print("-" * 80)
        print(self.get_proangler_report())
        print()

        # Source 2: FishingBooker
        print("🎯 FISHINGBOOKER CONDITIONS (Atlantic Beach)")
        print("-" * 80)
        print(self.get_fishingbooker_report())
        print()

        # Source 3: Tides4Fishing Atlantic Beach
        print("🌊 TIDES4FISHING - Atlantic Beach")
        print("-" * 80)
        print(self.get_tides4fishing_atlantic())
        print()

        # Source 4: Tides4Fishing Mayport (PRIMARY)
        print("⭐ TIDES4FISHING - Mayport Bar Pilots Dock (PRIMARY)")
        print("-" * 80)
        print(self.get_tides4fishing_mayport())
        print()

        # Source 5: NOAA Buoy
        print("🌐 NOAA BUOY MYPF1 (Mayport Bar Pilots Dock)")
        print("-" * 80)
        print(self.get_noaa_conditions())
        print()

        # Source 6: TideTime
        print("⏰ TIDETIME PREDICTIONS")
        print("-" * 80)
        print(self.get_tidetime_info())
        print()

        print(f"{'='*80}")
        print("✅ Report generation complete!")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        analyzer = FishingReportAnalyzer()
        analyzer.generate_report()
    except FileNotFoundError:
        print("❌ Error: config.json not found. Please ensure config.json is in the same directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        sys.exit(1)
