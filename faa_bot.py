import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import subprocess
import os
import gzip

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://aeronav.faa.gov/d-tpp/"

# AIRAC cycle effective dates are every 28 days.
# FAA d-TPP cycle IDs use YYMM format of the effective date.
# We probe recent cycles to find the active one.

def find_active_cycle():
    now = datetime.now()
    for offset in range(0, 8):
        d = now - timedelta(days=offset * 28)
        cycle = f"{str(d.year)[2:]}{str(d.month).zfill(2)}"
        url = f"{BASE_URL}{cycle}/xml_data/d-TPP_Metafile.xml"
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                print(f"  Aktiver Zyklus: {cycle}")
                return cycle, url
        except Exception:
            pass
    return None, None


def parse_metafile(cycle):
    url = f"{BASE_URL}{cycle}/xml_data/d-TPP_Metafile.xml"
    print(f"  Lade Metafile: {url}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()

    root = ET.fromstring(r.content)
    katalog = {}
    pdf_base = f"{BASE_URL}{cycle}/"

    for airport in root.iter('airport_name'):
        icao = (airport.get('icao_ident') or '').strip()
        apt  = (airport.get('apt_ident')  or '').strip()

        # Derive ICAO if missing: US airports use K + 3-letter FAA id
        if not icao and len(apt) == 3:
            icao = 'K' + apt

        if not icao or len(icao) != 4:
            continue

        karten = {}
        for record in airport.findall('record'):
            chart_name = (record.findtext('chart_name') or '').strip()
            pdf_name   = (record.findtext('pdf_name')   or '').strip()
            # Skip deleted/removed charts (pdf_name is literal "DELETED" for removed entries)
            if chart_name and pdf_name and pdf_name.upper() != 'DELETED':
                karten[chart_name] = pdf_base + pdf_name

        if karten:
            katalog[icao] = {
                '_url': pdf_base,
                'karten': karten
            }

    return katalog, cycle


def main():
    print("Suche aktiven FAA d-TPP Zyklus...")
    cycle, _ = find_active_cycle()
    if not cycle:
        print("Kein aktiver Zyklus gefunden.")
        return

    katalog, cycle = parse_metafile(cycle)
    print(f"  {len(katalog)} Flughäfen mit Karten gefunden.")

    out_path = os.path.join(REPO_DIR, "faa_katalog_export.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print("  JSON gespeichert.")

    git = r"C:\Program Files\Git\cmd\git.exe"
    subprocess.run([git, "-C", REPO_DIR, "add", "faa_katalog_export.json"], check=True)
    result = subprocess.run([git, "-C", REPO_DIR, "commit", "-m", f"FAA-Karten aktualisiert (Zyklus {cycle})"])
    if result.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("  GitHub aktualisiert.")
    else:
        print("  Keine Änderungen – kein Push nötig.")


if __name__ == "__main__":
    main()
