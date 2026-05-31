"""
cayman_bot.py – Cayman Islands AIP (Cayman Islands Airports Authority)
Liest AIP-Sections aus der Website; beide Airports teilen dieselben PDFs.
Ausgabe: mw_katalog_export.json
"""

import re, json, os, subprocess, requests
from bs4 import BeautifulSoup

AIP_PAGE = "https://www.caymanairports.com/aeronautical-information-publication"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "mw_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0", "Referer": AIP_PAGE}

AIRPORTS = {
    "MWCR": "Owen Roberts International Airport",
    "MWCB": "Charles Kirkconnell International Airport",
}

WANTED = {"General", "Enroute", "Aerodrome"}


def main():
    print("Lade Cayman Islands AIP ...")
    r = requests.get(AIP_PAGE, timeout=20, headers=HEADERS)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    karten = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" not in href.lower():
            continue
        txt = a.get_text(strip=True)
        if txt in WANTED:
            karten[f"AIP Cayman – {txt}"] = href
            print(f"  {txt}: {href.split('/')[-1][:60]}")

    if not karten:
        print("FEHLER: Keine AIP-PDFs gefunden!")
        return

    katalog = {
        icao: {"_url": AIP_PAGE, "karten": karten}
        for icao in AIRPORTS
    }
    print(f"\n{len(AIRPORTS)} Flughäfen, {len(karten)} Karten")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", "Cayman Islands AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
