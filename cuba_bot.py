"""
cuba_bot.py – Kuba AIP (ECNA – Empresa Cubana de Navegación Aérea)
Liest per-Airport AD-2 PDFs aus der statischen aip.html.
Ausgabe: mu_katalog_export.json
"""

import re, json, os, subprocess, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

AIP_PAGE = "https://aismet.avianet.cu/html/aip.html"
BASE_URL  = "https://aismet.avianet.cu"
REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = "mu_katalog_export.json"
HEADERS   = {"User-Agent": "Mozilla/5.0", "Referer": BASE_URL}

ICAO_RE = re.compile(r'(MU[A-Z]{2})', re.I)


def main():
    print("Lade Kuba AIP ...")
    r = requests.get(AIP_PAGE, timeout=20, headers=HEADERS)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    katalog = {}
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" not in href.lower():
            continue
        # Extract ICAO from the filename, not the full path
        fname = href.split("/")[-1]
        m = ICAO_RE.match(fname)
        if not m:
            continue
        icao = m.group(1).upper()
        if icao in seen:
            continue
        seen.add(icao)

        pdf_url = urljoin(AIP_PAGE, href)
        katalog[icao] = {
            "_url": AIP_PAGE,
            "karten": {"AIP Cuba – AD 2 (Aerodrome)": pdf_url},
        }
        print(f"  {icao}: {pdf_url}")

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
                         "-m", "Kuba AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
