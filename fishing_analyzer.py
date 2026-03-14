#!/usr/bin/env python3
"""Jacksonville ICW Fishing Report Analyzer — 7 APIs, 9 spots, seasonal species DB."""
import argparse
import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen

TZ = ZoneInfo("America/New_York")
LAT, LON = 30.3919, -81.4292
CONFIG_FILE = "config.json"

SEASONAL = {
    1:  {"hot": ["Sheepshead", "Black Drum"], "good": ["Redfish", "Seatrout"],
         "notes": "Winter creek fishing, sheepshead peak on pilings"},
    2:  {"hot": ["Sheepshead", "Black Drum"], "good": ["Redfish", "Flounder"],
         "notes": "Cold water, slow bite, fish deep structure"},
    3:  {"hot": ["Redfish", "Sheepshead"], "good": ["Seatrout", "Black Drum"],
         "notes": "Spring warmup, reds moving shallow"},
    4:  {"hot": ["Redfish", "Seatrout"], "good": ["Sheepshead", "Black Drum"],
         "notes": "Warming flats, topwater bite starts"},
    5:  {"hot": ["Redfish", "Seatrout", "Tarpon"], "good": ["Spanish Mackerel", "Black Drum"],
         "notes": "Tarpon arriving, live bait key"},
    6:  {"hot": ["Tarpon", "Snook", "Spanish Mackerel"], "good": ["Redfish", "Seatrout"],
         "notes": "Summer pattern, early/late best"},
    7:  {"hot": ["Tarpon", "Snook", "Spanish Mackerel"], "good": ["Redfish", "Seatrout"],
         "notes": "Peak summer, fish dawn/dusk"},
    8:  {"hot": ["Tarpon", "Snook", "Redfish"], "good": ["Seatrout", "Spanish Mackerel"],
         "notes": "Late summer, mullet staging"},
    9:  {"hot": ["Redfish", "Seatrout", "Bluefish"], "good": ["Flounder", "Black Drum"],
         "notes": "Mullet run begins, everything feeds"},
    10: {"hot": ["Redfish", "Bluefish", "Flounder"], "good": ["Seatrout", "Black Drum"],
         "notes": "Fall run peak, bull reds in passes"},
    11: {"hot": ["Redfish", "Seatrout", "Flounder"], "good": ["Sheepshead", "Black Drum"],
         "notes": "Cooling water, fish stacking in creeks"},
    12: {"hot": ["Sheepshead", "Black Drum", "Redfish"], "good": ["Seatrout", "Flounder"],
         "notes": "Winter pattern, structure fishing"},
}

SPECIES_PREFS = {
    "Redfish":          {"temp": (58, 82), "tide": "any",     "moon": "new/full", "months": range(1, 13)},
    "Seatrout":         {"temp": (55, 78), "tide": "falling", "moon": "any",      "months": range(1, 13)},
    "Sheepshead":       {"temp": (50, 72), "tide": "rising",  "moon": "any",      "months": [11, 12, 1, 2, 3, 4]},
    "Black Drum":       {"temp": (55, 80), "tide": "rising",  "moon": "new/full", "months": range(1, 13)},
    "Tarpon":           {"temp": (74, 90), "tide": "any",     "moon": "new/full", "months": [5, 6, 7, 8, 9]},
    "Snook":            {"temp": (70, 88), "tide": "any",     "moon": "any",      "months": [5, 6, 7, 8, 9]},
    "Spanish Mackerel": {"temp": (68, 85), "tide": "any",     "moon": "any",      "months": [5, 6, 7, 8, 9, 10]},
    "Bluefish":         {"temp": (58, 75), "tide": "falling", "moon": "any",      "months": [9, 10, 11]},
    "Flounder":         {"temp": (55, 78), "tide": "falling", "moon": "any",      "months": [2, 9, 10, 11, 12]},
    "Cobia":            {"temp": (65, 80), "tide": "any",     "moon": "any",      "months": [12, 1, 2, 3]},
}

SPOTS = [
    {"name": "Sisters Creek",               "wind_max": 25, "tide": "rising",  "seasons": [1,2,3,4,5,9,10,11,12],
     "why": "Protected bends, oyster bars, bait on incoming"},
    {"name": "Pablo Creek",                 "wind_max": 25, "tide": "falling", "seasons": list(range(1, 13)),
     "why": "Finger creeks drain = choke points, trout/reds ambush"},
    {"name": "Nassau Sound / Ft George",    "wind_max": 15, "tide": "any",     "seasons": [5,6,7,8,11,12,1,2],
     "why": "Exposed but tarpon summer, drum winter"},
    {"name": "Mayport Inlet / Jetties",     "wind_max": 20, "tide": "any",     "seasons": list(range(1, 13)),
     "why": "Deep water + jetty structure, current always helps"},
    {"name": "St Johns Confluence",         "wind_max": 20, "tide": "rising",  "seasons": list(range(1, 13)),
     "why": "Salinity break where river meets salt, fish stack"},
    {"name": "Dutton Island Preserve",      "wind_max": 25, "tide": "falling", "seasons": list(range(1, 13)),
     "why": "Sheltered flats, kayak-friendly, fish in pockets"},
    {"name": "Guana River / GTM Reserve",   "wind_max": 25, "tide": "rising",  "seasons": [3,4,5,9,10,11],
     "why": "Pristine flats, sight-casting reds"},
    {"name": "Ft George Island Bridges",    "wind_max": 20, "tide": "any",     "seasons": [11,12,1,2,3],
     "why": "Bridge pilings = current breaks, drum hold here"},
    {"name": "Amelia Island / Nassau River","wind_max": 20, "tide": "rising",  "seasons": list(range(1, 13)),
     "why": "Backwater creeks, bait funneled in"},
]

STATION_PRODUCTS = {
    "8720218": ["wind", "water_temperature", "air_temperature", "air_pressure"],
    "8720219": ["water_temperature"],
}

GO_LABELS = {75: "EXCELLENT", 55: "GOOD", 35: "FAIR", 0: "POOR"}


def _fetch_json(url: str, timeout: int = 10):
    req = Request(url, headers={"User-Agent": "JaxICWAnalyzer/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


class JaxICWAnalyzer:
    def __init__(self, json_mode=False):
        self.now = datetime.now(TZ)
        self.month = self.now.month
        self.data = {}
        self.json_mode = json_mode
        self.config = _load_config()

    def _fetch_tides(self, station, key):
        d0 = self.now.strftime("%Y%m%d")
        d1 = (self.now + timedelta(days=1)).strftime("%Y%m%d")
        return (key, _fetch_json(
            f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
            f"?begin_date={d0}&end_date={d1}&station={station}"
            f"&product=predictions&datum=MLLW&time_zone=lst_ldt"
            f"&interval=hilo&units=english&format=json"))

    def _fetch_coops_conditions(self, station, key):
        base = (f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
                f"?station={station}&date=latest&units=english"
                f"&time_zone=lst_ldt&format=json")
        products = STATION_PRODUCTS.get(station, ["water_temperature"])
        r = {}
        for prod in products:
            try:
                e = _fetch_json(f"{base}&product={prod}").get("data", [{}])[0]
                if prod == "wind":
                    r["wind_speed"] = f"{e.get('s', 'MM')} kts"
                    r["wind_dir"] = f"{e.get('dr', 'MM')} ({e.get('d', '')})"
                    r["wind_gust"] = f"{e.get('g', 'MM')} kts"
                elif prod == "water_temperature":
                    r["water_temp"] = f"{e.get('v', 'MM')} F"
                elif prod == "air_temperature":
                    r["air_temp"] = f"{e.get('v', 'MM')} F"
                elif prod == "air_pressure":
                    r["pressure"] = f"{e.get('v', 'MM')} mb"
            except Exception:
                pass
        return (key, r)

    def _fetch_pressure_trend(self):
        begin = (self.now - timedelta(hours=6)).strftime("%Y%m%d%%20%H:%M")
        end = self.now.strftime("%Y%m%d%%20%H:%M")
        url = (f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
               f"?station=8720218&begin_date={begin}&end_date={end}"
               f"&product=air_pressure&units=english&time_zone=lst_ldt&format=json")
        readings = _fetch_json(url).get("data", [])
        if len(readings) < 2:
            return ("pressure_trend", {"trend": "Unknown", "diff": 0})
        first = float(readings[0]["v"])
        last = float(readings[-1]["v"])
        diff = last - first
        if diff > 0.5:
            trend = "Rising"
        elif diff < -0.5:
            trend = "Falling"
        else:
            trend = "Steady"
        return ("pressure_trend", {"trend": trend, "diff": round(diff, 1),
                                   "first": first, "last": last})

    def _fetch_solunar(self):
        date_str = self.now.strftime("%Y%m%d")
        tz_offset = self.now.utcoffset().total_seconds() / 3600
        url = f"https://api.solunar.org/solunar/{LAT},{LON},{date_str},{int(tz_offset)}"
        return ("solunar", _fetch_json(url))

    def _fetch_sun(self):
        url = (f"https://api.sunrise-sunset.org/json?lat={LAT}&lng={LON}"
               f"&date={self.now.strftime('%Y-%m-%d')}&formatted=0")
        return ("sun", _fetch_json(url))

    def _fetch_marine(self):
        url = "https://api.weather.gov/gridpoints/JAX/73,64/forecast"
        data = _fetch_json(url)
        periods = data.get("properties", {}).get("periods", [])
        return ("marine", {"periods": periods})

    def fetch_all(self):
        fns = [
            lambda: self._fetch_tides("8720218", "tides_mayport"),
            lambda: self._fetch_tides("8720267", "tides_stjohns"),
            lambda: self._fetch_coops_conditions("8720218", "buoy_mayport"),
            lambda: self._fetch_coops_conditions("8720219", "buoy_dames"),
            self._fetch_pressure_trend,
            self._fetch_solunar,
            self._fetch_sun,
            self._fetch_marine,
        ]
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(f): f for f in fns}
            for fut in as_completed(futures):
                try:
                    k, v = fut.result()
                    self.data[k] = v
                except Exception as e:
                    print(f"  [WARN] {e}")

    # ── Data accessors ──────────────────────────────────────────────

    def _parse_float(self, src, key):
        raw = self.data.get(src, {}).get(key, "")
        try:
            return float(raw.split()[0])
        except (ValueError, IndexError):
            return None

    def _get_water_temp(self):
        for s in ("buoy_mayport", "buoy_dames"):
            v = self._parse_float(s, "water_temp")
            if v:
                return v
        return None

    def _get_wind_kts(self):
        return self._parse_float("buoy_mayport", "wind_speed")

    def _get_pressure_mb(self):
        p = self._parse_float("buoy_mayport", "pressure")
        return p if p and p > 900 else None

    def _get_pressure_trend(self):
        return self.data.get("pressure_trend", {}).get("trend", "Unknown")

    def _get_tide_direction(self):
        now_str = self.now.strftime("%Y-%m-%d %H:%M")
        for p in self.data.get("tides_mayport", {}).get("predictions", []):
            if p["t"] > now_str:
                return "rising" if p["type"] == "H" else "falling"
        return "unknown"

    def _get_moon_phase(self):
        return self.data.get("solunar", {}).get("moonPhase", "") or "unknown"

    def _solunar_minutes_to_next(self):
        """Returns (minutes_to_next_window, window_type) or (0, 'active') if inside one."""
        sol = self.data.get("solunar", {})
        if not sol:
            return (None, None)
        now_hm = self.now.hour * 60 + self.now.minute
        windows = []
        for label, sk, ek in [
            ("Major", "major1Start", "major1Stop"),
            ("Major", "major2Start", "major2Stop"),
            ("Minor", "minor1Start", "minor1Stop"),
            ("Minor", "minor2Start", "minor2Stop"),
        ]:
            start_str = sol.get(sk, "")
            stop_str = sol.get(ek, "")
            if not start_str or not stop_str:
                continue
            try:
                sh, sm = map(int, start_str.split(":"))
                eh, em = map(int, stop_str.split(":"))
                start_min = sh * 60 + sm
                end_min = eh * 60 + em
                windows.append((start_min, end_min, label))
            except ValueError:
                continue
        for start_min, end_min, label in windows:
            if start_min <= now_hm <= end_min:
                return (0, f"{label} (NOW)")
        future = []
        for start_min, end_min, label in windows:
            if start_min > now_hm:
                future.append((start_min - now_hm, label))
        if future:
            future.sort()
            return future[0]
        return (None, None)

    # ── Scoring ─────────────────────────────────────────────────────

    def score_species(self, name):
        prefs = SPECIES_PREFS.get(name)
        if not prefs:
            return 0
        s = 50
        wt = self._get_water_temp()
        if wt and prefs["temp"][0] <= wt <= prefs["temp"][1]:
            s += 20
        tide = self._get_tide_direction()
        if prefs["tide"] == "any" or prefs["tide"] == tide:
            s += 15
        if self._get_pressure_trend() == "Falling":
            s += 10
        mins, _ = self._solunar_minutes_to_next()
        if mins is not None:
            if mins == 0:
                s += 10
            elif mins <= 60:
                s += 7
            elif mins <= 180:
                s += 3
        moon = self._get_moon_phase().lower()
        if prefs["moon"] == "new/full" and ("new" in moon or "full" in moon):
            s += 10
        elif prefs["moon"] == "any":
            s += 5
        season = SEASONAL.get(self.month, {})
        if name in season.get("hot", []):
            s += 10
        elif name in season.get("good", []):
            s += 5
        wind = self._get_wind_kts()
        if wind and wind > 15:
            s -= 10
        return max(0, min(100, s))

    def score_spot(self, spot):
        s = 0
        wind = self._get_wind_kts()
        if wind is not None:
            if wind <= spot["wind_max"] * 0.6:
                s += 30
            elif wind <= spot["wind_max"]:
                s += 20
            else:
                s -= 10
        else:
            s += 15
        tide = self._get_tide_direction()
        if spot["tide"] == tide:
            s += 20
        elif spot["tide"] == "any":
            s += 12
        if self.month in spot["seasons"]:
            s += 20
        else:
            s -= 5
        mins, _ = self._solunar_minutes_to_next()
        if mins is not None and mins <= 60:
            s += 15
        elif mins is not None and mins <= 180:
            s += 8
        wt = self._get_water_temp()
        if wt and 55 <= wt <= 85:
            s += 15
        return max(0, min(100, s))

    def go_no_go(self):
        wind = self._get_wind_kts()
        wt = self._get_water_temp()
        moon = self._get_moon_phase().lower()
        mins, _ = self._solunar_minutes_to_next()
        f = {
            "Wind": max(0, 25 - int(wind)) if wind is not None else 15,
            "Water Temp": (20 if 55 <= wt <= 85 else (10 if 50 <= wt <= 90 else 0)) if wt else 10,
            "Tide Movement": 15 if self._get_tide_direction() in ("rising", "falling") else 5,
            "Pressure": 15 if self._get_pressure_trend() == "Falling" else (10 if self._get_pressure_trend() == "Steady" else 8),
            "Solunar": 15 if (mins is not None and mins <= 60) else (10 if mins is not None and mins <= 180 else 7),
            "Moon Phase": 10 if ("new" in moon or "full" in moon) else 5,
        }
        return sum(f.values()), f

    # ── Report output ───────────────────────────────────────────────

    def print_header(self):
        tz_abbr = self.now.strftime("%Z")
        print(f"\n{'='*80}")
        print(f"  JACKSONVILLE ICW FISHING REPORT")
        print(f"  {LAT}N, {LON}W")
        print(f"  Generated: {self.now.strftime('%Y-%m-%d %I:%M %p')} {tz_abbr}")
        print(f"{'='*80}")

    def print_tides(self):
        print(f"\n--- TIDES {'—'*68}")
        for label, key in [("Mayport (8720218)", "tides_mayport"),
                           ("St Johns (8720267)", "tides_stjohns")]:
            preds = self.data.get(key, {}).get("predictions", [])
            if not preds:
                print(f"  {label}: [UNAVAILABLE]")
                continue
            print(f"  {label}:")
            for p in preds:
                kind = "HIGH" if p["type"] == "H" else "LOW "
                print(f"    {kind}  {p['t']}  {p['v']} ft")
        print(f"  Status: {self._get_tide_direction().upper()}")

    def print_solunar(self):
        print(f"\n--- MOON & SOLUNAR {'—'*60}")
        sol = self.data.get("solunar", {})
        if not sol:
            print("  [UNAVAILABLE]")
            return
        illum = sol.get("moonIllumination", 0)
        print(f"  Moon: {sol.get('moonPhase', '?')} ({illum:.0f}% illumination)")
        for lbl, sk, ek in [("Major 1", "major1Start", "major1Stop"),
                            ("Major 2", "major2Start", "major2Stop"),
                            ("Minor 1", "minor1Start", "minor1Stop"),
                            ("Minor 2", "minor2Start", "minor2Stop")]:
            s, e = sol.get(sk), sol.get(ek)
            if s and e:
                print(f"  {lbl}: {s} - {e}")
        mins, wtype = self._solunar_minutes_to_next()
        if mins is not None:
            if mins == 0:
                print(f"  >> {wtype} <<")
            else:
                hrs = mins // 60
                remaining = mins % 60
                print(f"  Next window: {wtype} in {hrs}h {remaining}m")

    def print_conditions(self):
        print(f"\n--- CONDITIONS {'—'*64}")
        for label, key in [("Mayport (8720218)", "buoy_mayport"),
                           ("Dames Point (8720219)", "buoy_dames")]:
            b = self.data.get(key)
            if not b:
                print(f"  {label}: [UNAVAILABLE]")
                continue
            fields = [("Water", "water_temp"), ("Air", "air_temp"), ("Wind", "wind_speed"),
                      ("Gust", "wind_gust"), ("Dir", "wind_dir"), ("Baro", "pressure")]
            parts = [f"{n} {b[k]}" for n, k in fields if b.get(k) and "MM" not in b[k]]
            print(f"  {label}: {' | '.join(parts) if parts else '[NO DATA]'}")
        pt = self.data.get("pressure_trend", {})
        if pt.get("trend"):
            print(f"  Pressure trend (6hr): {pt['trend']} ({pt.get('diff', 0):+.1f} mb)")

    def print_weather(self):
        print(f"\n--- WEATHER FORECAST (JAX) {'—'*52}")
        periods = self.data.get("marine", {}).get("periods", [])
        if not periods:
            print("  [UNAVAILABLE]")
            return
        for p in periods[:2]:
            detail = p.get("detailedForecast") or p.get("shortForecast", "")
            print(f"  {p.get('name', '')}: {detail[:200]}")

    def print_species(self):
        print(f"\n--- SPECIES OUTLOOK {'—'*59}")
        season = SEASONAL.get(self.month, {})
        print(f"  Season: {season.get('notes', '')}")
        active = set(season.get("hot", []) + season.get("good", []))
        for name in sorted(SPECIES_PREFS):
            if name not in active and self.month not in SPECIES_PREFS[name]["months"]:
                continue
            s = self.score_species(name)
            tag = "HOT" if name in season.get("hot", []) else "   "
            print(f"  [{tag}] {name:<20s} {s:>3d}/100  {'#' * (s // 5)}")

    def print_spots(self):
        print(f"\n--- ALL SPOTS RANKED {'—'*58}")
        ranked = sorted(SPOTS, key=lambda sp: self.score_spot(sp), reverse=True)
        for i, spot in enumerate(ranked, 1):
            s = self.score_spot(spot)
            print(f"  {i}. {spot['name']:<32s} {s:>3d}/100  {spot['why']}")

    def print_windows(self):
        print(f"\n--- BEST WINDOWS {'—'*62}")
        sun = self.data.get("sun", {}).get("results", {})
        sol = self.data.get("solunar", {})
        windows = []
        for key, label in [("civil_twilight_begin", "Dawn"), ("civil_twilight_end", "Dusk")]:
            if sun.get(key):
                try:
                    t = datetime.fromisoformat(sun[key]).astimezone(TZ)
                    windows.append(f"{label + ':':<12s}{t.strftime('%I:%M %p')}")
                except Exception:
                    pass
        for label, sk, ek in [("Major 1", "major1Start", "major1Stop"),
                              ("Major 2", "major2Start", "major2Stop")]:
            s, e = sol.get(sk, ""), sol.get(ek, "")
            if s and e:
                windows.append(f"Solunar {label}: {s} - {e}")
        preds = self.data.get("tides_mayport", {}).get("predictions", [])
        now_str = self.now.strftime("%Y-%m-%d %H:%M")
        for p in preds:
            if p["t"] > now_str:
                kind = "High" if p["type"] == "H" else "Low"
                windows.append(f"Next {kind} Tide: {p['t']} ({p['v']} ft)")
                break
        if windows:
            for w in windows:
                print(f"  {w}")
            print("  Tip: Best bite = tide transition + solunar overlap + low-light")
        else:
            print("  [UNAVAILABLE]")

    def print_go_no_go(self):
        print(f"\n--- GO / NO-GO {'—'*64}")
        total, factors = self.go_no_go()
        label = next(v for k, v in sorted(GO_LABELS.items(), reverse=True) if total >= k)
        print(f"  VERDICT: {label} ({total}/100)")
        for k, v in factors.items():
            print(f"    {k:<15s} {v:>3d} pts")

    # ── JSON output ─────────────────────────────────────────────────

    def build_json(self):
        ranked_spots = sorted(SPOTS, key=lambda sp: self.score_spot(sp), reverse=True)
        season = SEASONAL.get(self.month, {})
        active = set(season.get("hot", []) + season.get("good", []))
        species_scores = {}
        for name in sorted(SPECIES_PREFS):
            if name in active or self.month in SPECIES_PREFS[name]["months"]:
                species_scores[name] = {
                    "score": self.score_species(name),
                    "hot": name in season.get("hot", []),
                }
        total, factors = self.go_no_go()
        return {
            "generated": self.now.isoformat(),
            "location": {"lat": LAT, "lon": LON},
            "tides": {
                "mayport": self.data.get("tides_mayport", {}),
                "stjohns": self.data.get("tides_stjohns", {}),
                "direction": self._get_tide_direction(),
            },
            "solunar": self.data.get("solunar", {}),
            "conditions": {
                "mayport": self.data.get("buoy_mayport", {}),
                "dames_point": self.data.get("buoy_dames", {}),
                "pressure_trend": self.data.get("pressure_trend", {}),
            },
            "weather": self.data.get("marine", {}),
            "species": species_scores,
            "spots": [
                {"name": sp["name"], "score": self.score_spot(sp), "why": sp["why"]}
                for sp in ranked_spots
            ],
            "go_no_go": {"total": total, "label": next(
                v for k, v in sorted(GO_LABELS.items(), reverse=True) if total >= k
            ), "factors": factors},
        }

    # ── Main ────────────────────────────────────────────────────────

    def run(self):
        if not self.json_mode:
            self.print_header()
            print("\nFetching live data from 8 sources...")
        self.fetch_all()
        if self.json_mode:
            print(json.dumps(self.build_json(), indent=2, default=str))
        else:
            self.print_tides()
            self.print_solunar()
            self.print_conditions()
            self.print_weather()
            self.print_species()
            self.print_spots()
            self.print_windows()
            self.print_go_no_go()
            print(f"\n{'='*80}\n  Report complete.\n{'='*80}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jacksonville ICW Fishing Report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    try:
        JaxICWAnalyzer(json_mode=args.json).run()
    except KeyboardInterrupt:
        print("\nAborted.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
