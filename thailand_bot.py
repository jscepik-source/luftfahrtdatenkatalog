"""
thailand_bot.py – Thailand AIP (CAAT, aip.caat.or.th)
Erkennt die aktuelle AIRAC-Periode automatisch, kein Selenium nötig.
Ausgabe: vt_katalog_export.json
"""

import re, json, os, subprocess, requests
from datetime import date
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT_URL = "https://aip.caat.or.th/"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "vt_katalog_export.json"


def find_current_airac():
    """Liest alle AIRAC-Zyklen von der Root-Seite und gibt den aktuellen zurück."""
    r = requests.get(ROOT_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    cycles = sorted(set(re.findall(r'(\d{4}-\d{2}-\d{2})-AIRAC', r.text)))
    today = date.today().isoformat()
    current = None
    for c in cycles:
        if c <= today:
            current = c
    return current


def scrape_airport(base_url, icao):
    """Gibt alle Chart-Namen → PDF-URLs für einen Flughafen zurück."""
    page_url = f"{base_url}/html/eAIP/VT-AD-2.{icao}-en-GB.html"
    try:
        r = requests.get(page_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        karten = {}
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "graphics/" in href and href.endswith(".pdf"):
                name = a.get_text(strip=True)
                if name:
                    karten[name] = urljoin(page_url, href)
        return karten
    except Exception as e:
        print(f"    {icao}: Fehler – {e}")
        return {}


def main():
    print("Suche aktuelle AIRAC-Periode ...")
    cycle = find_current_airac()
    if not cycle:
        print("FEHLER: Keine AIRAC-Periode auf der Root-Seite gefunden!")
        return

    base_url = ROOT_URL.rstrip("/") + "/" + cycle + "-AIRAC"
    print(f"  Aktuelle Periode: {cycle}")
    print(f"  Base URL:         {base_url}")

    # ── Alle Flughäfen aus dem Menü ─────────────────────────────────────────
    menu_url = f"{base_url}/html/eAIP/VT-menu-en-GB.html"
    r = requests.get(menu_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    icao_codes = sorted(set(re.findall(r"VT-AD-2\.([A-Z]{4})", r.text)))
    print(f"  {len(icao_codes)} Flughäfen im Menü")

    # ── Karten je Flughafen ─────────────────────────────────────────────────
    katalog = {}
    for i, icao in enumerate(icao_codes, 1):
        karten = scrape_airport(base_url, icao)
        ap_url  = f"{base_url}/html/eAIP/VT-AD-2.{icao}-en-GB.html"
        print(f"  [{i:2d}/{len(icao_codes)}] {icao}: {len(karten)} Karten", flush=True)
        if karten:
            katalog[icao] = {"_url": ap_url, "karten": karten}

    print(f"\n  Gesamt: {len(katalog)} Flughäfen mit Karten")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r = subprocess.run([git, "-C", REPO_DIR, "commit",
                        "-m", f"Thailand AIP (CAAT, {cycle}) aktualisiert"])
    if r.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
