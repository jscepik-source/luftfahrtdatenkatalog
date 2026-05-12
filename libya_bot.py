"""
libya_bot.py – Libyen AIP (CAA Libya)
Liest per-Airport AD-Karten aus der AIS-Website.
Ausgabe: hl_katalog_export.json
"""

import re, json, os, subprocess, requests
from bs4 import BeautifulSoup

AD_PAGE  = "https://caa.gov.ly/ais/ad/"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "hl_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0", "Referer": AD_PAGE}

ICAO_RE = re.compile(r'\b(HL[A-Z]{2})\b', re.I)


def main():
    print("Lade Libyen AIP ...")
    r = requests.get(AD_PAGE, timeout=20, headers=HEADERS)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    katalog = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" not in href.lower():
            continue
        link_text = a.get_text(strip=True)
        m = ICAO_RE.search(link_text)
        if not m:
            continue
        icao = m.group(1).upper()

        # Derive chart label from section prefix
        sec = re.match(r'^(AD\s*\d)', link_text, re.I)
        if sec and '3' in sec.group(1):
            chart_name = "AD 3 – Other Aerodrome"
        else:
            chart_name = "AD 2 – Aerodrome"

        if icao not in katalog:
            katalog[icao] = {"_url": AD_PAGE, "karten": {}}
        katalog[icao]["karten"][chart_name] = href
        print(f"  {icao}: {chart_name} -> {href.split('/')[-1]}")

    print(f"\n{len(katalog)} Flughäfen gefunden.")
    if not katalog:
        print("FEHLER: Keine Flughäfen gefunden!")
        return

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", "Libyen AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
