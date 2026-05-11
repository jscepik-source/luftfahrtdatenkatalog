"""
albania_bot.py – Albanien AIP (Albcontrol, albcontrol.al)
Erkennt aktuelle AIRAC-Periode automatisch, kein Selenium nötig.
Ausgabe: la_katalog_export.json
"""

import re, json, os, subprocess, requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

AIP_INDEX = "https://albcontrol.al/wp-web/aip/"
BASE_HOST = "https://www.albcontrol.al"
REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = "la_katalog_export.json"
HEADERS   = {"User-Agent": "Mozilla/5.0"}

MONTHS = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
          "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}


def parse_mon_date(s):
    """'16-APR-2026' → datetime"""
    m = re.match(r"(\d{2})-([A-Z]{3})-(\d{4})", s)
    return datetime(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))) if m else None


def find_current_airac():
    """Liest Albcontrol-AIP-Seite und gibt (folder_name, iso_date) zurück."""
    r = requests.get(AIP_INDEX, timeout=15, headers=HEADERS)
    # z.B. "16-APR-2026-A" und "2026-04-16-AIRAC"
    folders = re.findall(r'(\d{2}-[A-Z]{3}-\d{4}-A)', r.text)
    today = datetime.today()
    best, best_dt = None, None
    for f in set(folders):
        dt = parse_mon_date(f[:-2])
        if dt and dt <= today and (best_dt is None or dt > best_dt):
            best, best_dt = f, dt
    if not best:
        return None, None
    iso = best_dt.strftime("%Y-%m-%d")
    return best, iso   # e.g. ("16-APR-2026-A", "2026-04-16")


def scrape_airport(base_url, icao):
    """Gibt {chart_name: pdf_url} für einen Flughafen zurück."""
    page_url = f"{base_url}/html/eAIP/LA-AD-2.{icao}-en-GB.html"
    try:
        r = requests.get(page_url, timeout=20, headers=HEADERS)
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        karten = {}

        # Chart-Name steht im ersten <td> des nächsten <tr> nach dem PDF-Link
        pdf_re = re.compile(r"\.\./graphics/eAIP/[^\"]+\.pdf")
        for a in soup.find_all("a", href=pdf_re):
            pdf_url = urljoin(page_url, a["href"])
            # Chart-Name: nächste <td> mit Text in der folgenden Zeile
            chart_name = ""
            tr = a.find_parent("tr")
            if tr:
                next_tr = tr.find_next_sibling("tr")
                if next_tr:
                    td = next_tr.find("td")
                    if td:
                        chart_name = td.get_text(strip=True)
            if not chart_name:
                # Fallback: Dateiname ohne Pfad
                chart_name = a["href"].split("/")[-1]
            karten[chart_name] = pdf_url

        return karten
    except Exception as e:
        print(f"    {icao}: Fehler – {e}")
        return {}


def main():
    print("Suche aktuelle AIRAC-Periode ...")
    folder, iso_date = find_current_airac()
    if not folder:
        print("FEHLER: Keine aktuelle AIRAC-Periode gefunden!")
        return

    base_url = f"{BASE_HOST}/al/aip/{folder}/{iso_date}-AIRAC"
    print(f"  Periode: {folder}  ({iso_date})")
    print(f"  Base:    {base_url}")

    # ── Flughäfen aus dem Menü ───────────────────────────────────────────────
    menu_url = f"{base_url}/html/eAIP/LA-menu-en-GB.html"
    r = requests.get(menu_url, timeout=15, headers=HEADERS)
    icao_codes = sorted(set(re.findall(r"LA-AD-2\.([A-Z]{4})", r.text)))
    print(f"  {len(icao_codes)} Flughäfen: {icao_codes}")

    # ── Karten je Flughafen ─────────────────────────────────────────────────
    katalog = {}
    for icao in icao_codes:
        karten = scrape_airport(base_url, icao)
        ap_url = f"{base_url}/html/eAIP/LA-AD-2.{icao}-en-GB.html"
        print(f"  {icao}: {len(karten)} Karten")
        if karten:
            katalog[icao] = {"_url": ap_url, "karten": karten}

    print(f"\n  Gesamt: {len(katalog)} Flughäfen")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", f"Albanien AIP ({folder}) aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
