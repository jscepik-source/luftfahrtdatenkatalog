"""
cyprus_bot.py – Zypern AIP (DCAC, mcw.gov.cy)
Parst aktuellen AIRAC-Amendment-Download-Link (sync.com).
Ausgabe: lc_katalog_export.json
"""

import re, json, os, subprocess, warnings, requests
from datetime import datetime
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")  # SSL-Zertifikatwarnung unterdrücken

AIP_URL  = ("https://www.mcw.gov.cy/mcw/DCA/AIS/ais.nsf/All/"
            "57B39BFA3276159CC2257C7E00233AA2?OpenDocument")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "lc_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0"}

MONTHS = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
          "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

AIRPORTS = ["LCLK", "LCPH"]


def parse_date(s):
    """'19 FEB 2026' → datetime"""
    m = re.match(r"(\d{1,2})\s+([A-Z]{3})\s+(\d{4})", s.strip())
    return datetime(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))) if m else None


def find_current_amdt():
    """Gibt (label, sync_url, eff_date) des aktuell gültigen Amendments zurück."""
    r = requests.get(AIP_URL, timeout=20, headers=HEADERS, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    today = datetime.today()

    best_url, best_date, best_label = None, None, None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "sync.com" not in href or not a.get_text(strip=True):
            continue
        label = a.get_text(strip=True)
        tr = a.find_parent("tr")
        if not tr:
            continue
        row_text = tr.get_text(separator=" ", strip=True)
        m = re.search(r"(\d{1,2}\s+[A-Z]{3}\s+\d{4})", row_text)
        if not m:
            continue
        dt = parse_date(m.group(1))
        if dt and dt <= today:
            if best_date is None or dt > best_date:
                best_date, best_url, best_label = dt, href, label

    return best_label, best_url, best_date


def main():
    print("Suche aktuellen Zypern-AIP-Amendment ...")
    label, sync_url, eff_date = find_current_amdt()
    if not sync_url:
        print("FEHLER: Kein gültiger AIRAC-Amendment gefunden!")
        return

    print(f"  Amendment: {label}  (gültig ab {eff_date.strftime('%d %b %Y')})")
    print(f"  Download:  {sync_url}")

    karten = {label: sync_url}
    katalog = {
        icao: {"_url": AIP_URL, "karten": karten}
        for icao in AIRPORTS
    }
    print(f"  {len(AIRPORTS)} Flughäfen: {AIRPORTS}")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", f"Zypern AIP ({label}) aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
