"""
russia_bot.py – Russland AIP (CAICA, www.caica.ru)
Parst das statische HTML-Menü ohne Selenium.
Ausgabe: u_katalog_export.json
"""

import re, json, os, subprocess, requests

MENU_URL = "https://www.caica.ru/common/AirInter/validaip/html/menueng.htm"
BASE_URL = "https://www.caica.ru/common/AirInter/validaip"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "u_katalog_export.json"

# ItemLink("../aip/ad/ad2/uuee/datei.pdf","Name")
LINK_RE  = re.compile(
    r'ItemLink\("(\.\./aip/ad/ad2/([a-z]{4})/([^"]+))","([^"]+)"\)',
    re.IGNORECASE
)
# ItemBegin("id","url","UUEE SHEREMETYEVO") – Flughafen-Namen
BEGIN_RE = re.compile(
    r'ItemBegin\("[^"]*","[^"]*","([A-Z]{4}[^"]+)"\)'
)


def resolve(rel_path):
    """../aip/... → https://base/aip/..."""
    return BASE_URL + '/' + rel_path.lstrip('./').lstrip('/')


def main():
    print(f"Lade {MENU_URL} ...")
    resp = requests.get(MENU_URL, timeout=30,
                        headers={'User-Agent': 'Mozilla/5.0'})
    resp.encoding = 'windows-1251'
    content = resp.text

    # ── Flughafen-Namen aus ItemBegin ────────────────────────────────────────
    namen = {}
    for m in BEGIN_RE.finditer(content):
        name = m.group(1).strip()
        icao = name[:4].upper()
        if re.match(r'^[A-Z]{4}$', icao):
            namen[icao] = name

    # ── Chart-Links aus AD-2-Bereich ─────────────────────────────────────────
    katalog = {}
    for m in LINK_RE.finditer(content):
        rel_path   = m.group(1)
        icao       = m.group(2).upper()
        chart_name = m.group(4).strip()
        pdf_url    = resolve(rel_path)

        if icao not in katalog:
            ordner_url = BASE_URL + '/aip/ad/ad2/' + icao.lower() + '/'
            katalog[icao] = {
                '_url':  ordner_url,
                'name':  namen.get(icao, icao),
                'karten': {}
            }
        katalog[icao]['karten'][chart_name] = pdf_url

    print(f"{len(katalog)} Flughäfen gefunden")
    for icao, data in sorted(katalog.items())[:5]:
        print(f"  {icao} ({data['name']}): {len(data['karten'])} Karten")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, '-C', REPO_DIR, 'add', OUTPUT], check=True)
    r = subprocess.run([git, '-C', REPO_DIR, 'commit',
                        '-m', 'Russland AIP (CAICA) aktualisiert'])
    if r.returncode == 0:
        subprocess.run([git, '-C', REPO_DIR, 'push'], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == '__main__':
    main()
