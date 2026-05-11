"""
bhutan_bot.py – Bhutan AIP (DOAT – Dept. of Air Transport)
Liest per-Airport AD-Karten aus der statischen AIP-Seite.
Ausgabe: vq_katalog_export.json
"""

import re, json, os, subprocess, requests
from bs4 import BeautifulSoup

AIP_PAGE = "https://www.doat.gov.bt/aip/"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "vq_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0", "Referer": AIP_PAGE}

ICAO_RE = re.compile(r'\b(VQ[A-Z]{2})\b', re.I)


def main():
    print("Lade Bhutan AIP ...")
    r = requests.get(AIP_PAGE, timeout=20, headers=HEADERS)
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
            m = ICAO_RE.search(href)
        if not m:
            continue
        icao = m.group(1).upper()

        chart_name = re.sub(r'\s*-?\s*' + icao, '', link_text, flags=re.I).strip()
        chart_name = re.sub(r'^AD\d+_\d+\s*', '', chart_name).strip() or "AD 2 – Aerodrome"

        if icao not in katalog:
            katalog[icao] = {"_url": AIP_PAGE, "karten": {}}
        katalog[icao]["karten"][chart_name] = href
        print(f"  {icao}: {chart_name[:60]} -> {href.split('/')[-1]}")

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
                         "-m", "Bhutan AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
