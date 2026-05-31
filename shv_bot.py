"""
SHV/FSVL Airspace Bot
Laedt Schweizer Luftraumdaten (OpenAir-Format) von airspace.shv-fsvl.ch
und konvertiert sie nach GeoJSON fuer die Leaflet-Karte.
"""
import requests, json, re, math
from datetime import datetime, timezone

SHV_BASE = "https://airspace.shv-fsvl.ch/downloads"
FILES = {
    "airspace": f"{SHV_BASE}/switzerland-airspace-feet.txt",
    "wildlife": f"{SHV_BASE}/switzerland-wildlife-feet.txt",
}

KLASSEN_FARBE = {
    "A":"#dc2626","B":"#ea580c","C":"#2563eb","D":"#16a34a",
    "E":"#ca8a04","F":"#7c3aed","G":"#64748b",
    "CTR":"#16a34a","TMA":"#2563eb","R":"#dc2626","P":"#7f1d1d",
    "D_AREA":"#ea580c","W":"#84cc16","OTHER":"#94a3b8"
}

def dms_to_dd(dms_str):
    """Dezimalgrad aus DMS (47:28:24 N oder 008:33:24 E)"""
    m = re.match(r'(\d+):(\d+):(\d+)\s*([NSEW])', dms_str.strip())
    if not m:
        return None
    d, mn, s, hem = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    dd = d + mn/60 + s/3600
    if hem in ('S','W'):
        dd = -dd
    return dd

def arc_points(cx, cy, r_nm, start_deg, end_deg, clockwise=True, steps=32):
    """Punkte entlang eines Kreisbogens"""
    r_deg = r_nm / 60.0
    if clockwise:
        if end_deg < start_deg:
            end_deg += 360
    else:
        if end_deg > start_deg:
            start_deg += 360
        start_deg, end_deg = end_deg, start_deg
    pts = []
    for i in range(steps + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
        pts.append([cx + r_deg * math.sin(a), cy + r_deg * math.cos(a)])
    return pts

def parse_openair(text):
    features = []
    current = None
    cx, cy, r_nm = None, None, None
    clockwise = True

    for raw_line in text.splitlines():
        line = raw_line.split('*')[0].strip()
        if not line:
            continue

        if line.startswith('AC '):
            if current and len(current['geometry']['coordinates'][0]) >= 3:
                current['geometry']['coordinates'][0].append(
                    current['geometry']['coordinates'][0][0])
                features.append(current)
            klasse = line[3:].strip().upper()
            color = KLASSEN_FARBE.get(klasse, KLASSEN_FARBE['OTHER'])
            current = {
                "type": "Feature",
                "properties": {"class": klasse, "name": "", "upper": "", "lower": "", "color": color},
                "geometry": {"type": "Polygon", "coordinates": [[]]}
            }
            cx = cy = r_nm = None
            clockwise = True

        elif current is None:
            continue

        elif line.startswith('AN '):
            current['properties']['name'] = line[3:].strip()

        elif line.startswith('AH '):
            current['properties']['upper'] = line[3:].strip()

        elif line.startswith('AL '):
            current['properties']['lower'] = line[3:].strip()

        elif line.startswith('DP '):
            parts = line[3:].strip().split()
            coords_str = ' '.join(parts)
            pts = re.findall(r'(\d+:\d+:\d+\s*[NS])\s+(\d+:\d+:\d+\s*[EW])', coords_str)
            if pts:
                lat = dms_to_dd(pts[0][0])
                lon = dms_to_dd(pts[0][1])
                if lat is not None and lon is not None:
                    current['geometry']['coordinates'][0].append([lon, lat])

        elif line.startswith('V X='):
            pts = re.findall(r'(\d+:\d+:\d+\s*[NS])\s+(\d+:\d+:\d+\s*[EW])', line)
            if pts:
                cy = dms_to_dd(pts[0][0])
                cx = dms_to_dd(pts[0][1])

        elif line.startswith('V D='):
            clockwise = '+' in line

        elif line.startswith('DC '):
            try:
                r_nm = float(line[3:].strip())
                if cx and cy:
                    for i in range(33):
                        a = math.radians(i * 360 / 32)
                        lat = cy + (r_nm/60) * math.cos(a)
                        lon = cx + (r_nm/60) * math.sin(a)
                        current['geometry']['coordinates'][0].append([lon, lat])
            except:
                pass

        elif line.startswith('DB '):
            pts = re.findall(r'(\d+:\d+:\d+\s*[NS])\s+(\d+:\d+:\d+\s*[EW])', line)
            if len(pts) >= 2 and cx and cy:
                lat1 = dms_to_dd(pts[0][0]); lon1 = dms_to_dd(pts[0][1])
                lat2 = dms_to_dd(pts[1][0]); lon2 = dms_to_dd(pts[1][1])
                if None not in (lat1, lon1, lat2, lon2):
                    a1 = math.degrees(math.atan2(lon1 - cx, lat1 - cy))
                    a2 = math.degrees(math.atan2(lon2 - cx, lat2 - cy))
                    r  = math.sqrt((lon1-cx)**2 + (lat1-cy)**2) * 60
                    for pt in arc_points(cx, cy, r, a1, a2, clockwise):
                        current['geometry']['coordinates'][0].append(pt)

    if current and len(current['geometry']['coordinates'][0]) >= 3:
        current['geometry']['coordinates'][0].append(current['geometry']['coordinates'][0][0])
        features.append(current)

    return {"type": "FeatureCollection", "features": features}

def main():
    headers = {"User-Agent": "Mozilla/5.0"}
    results = {}
    for key, url in FILES.items():
        print(f"Lade {url} ...")
        res = requests.get(url, headers=headers, timeout=20)
        res.raise_for_status()
        geo = parse_openair(res.text)
        results[key] = {"url": url, "features": len(geo["features"])}
        fname = f"shv_{key}.geojson"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(geo, f, separators=(',',':'))
        print(f"  {fname}: {len(geo['features'])} Features")

    meta = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": results
    }
    with open("shv_latest.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Fertig:", meta)

if __name__ == "__main__":
    main()
