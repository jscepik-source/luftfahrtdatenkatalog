"""
nepal_bot.py – Nepal AIP (CAAN – Civil Aviation Authority of Nepal)
Liest per-Airport AD-Karten aus der AIP-Liste.
Ausgabe: vn_katalog_export.json
"""

import re, json, os, subprocess, requests
from bs4 import BeautifulSoup

AIP_LIST  = "https://e-aip.caanepal.gov.np/welcome/listall/1"
AIP_PAGE  = "https://e-aip.caanepal.gov.np/"
REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = "vn_katalog_export.json"
HEADERS   = {"User-Agent": "Mozilla/5.0", "Referer": AIP_PAGE}

ICAO_RE = re.compile(r'^(VN[A-Z]{2})$', re.I)


def main():
    print("Lade Nepal AIP ...")
    r = requests.get(AIP_LIST, timeout=20, headers=HEADERS)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    katalog = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" not in href.lower():
            continue
        link_text = a.get_text(strip=True)
        m = ICAO_RE.match(link_text)
        if not m:
            continue
        icao = m.group(1).upper()
        if icao in katalog:
            continue

        katalog[icao] = {
            "_url": AIP_LIST,
            "karten": {"AIP Nepal – AD 2 (Aerodrome)": href},
        }
        print(f"  {icao}: {href.split('/')[-1]}")

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
                         "-m", "Nepal AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
