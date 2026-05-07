"""
austrocontrol_bot.py – Scraper für das Austrocontrol eAIP (Österreich / LO)
Kein Selenium nötig – die Seiten sind reines HTML.
Ausgabe: lo_katalog_export.json (kompatibel mit dem DFS-Katalogformat)
"""

import re, json, os, subprocess
import requests
from html.parser import HTMLParser

REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
BASIS_URL = "https://eaip.austrocontrol.at/"
AUSGABE   = "lo_katalog_export.json"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; AIPBot/1.0)"})


class LinkParser(HTMLParser):
    """Einfacher HTML-Parser der alle <a href> + Linktext sammelt."""
    def __init__(self):
        super().__init__()
        self.links = []      # [(text, href), ...]
        self._current_href = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            self._current_href = attrs_dict.get("href", "")
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "a" and self._current_href is not None:
            self.links.append((
                "".join(self._buf).strip(),
                self._current_href,
            ))
            self._current_href = None

    def handle_data(self, data):
        if self._current_href is not None:
            self._buf.append(data)


def seite_laden(url, timeout=20):
    r = SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    parser = LinkParser()
    parser.feed(r.text)
    return parser.links


def aktuelle_edition_basis():
    """Gibt die Basis-URL der aktuellen AIP-Ausgabe zurück, z.B.
    'https://eaip.austrocontrol.at/lo/260417/'"""
    links = seite_laden(BASIS_URL)
    for _, href in links:
        m = re.search(r'lo/(\d{6})/index\.htm', href)
        if m:
            return f"{BASIS_URL}lo/{m.group(1)}/"
    raise RuntimeError("Aktuelle AIP-Edition nicht gefunden")


def flughafen_icao_codes(basis):
    """Liest die AD-2-Übersichtsseite und gibt alle österreichischen ICAO-Codes zurück."""
    links = seite_laden(basis + "ad_2.htm")
    codes = []
    for _, href in links:
        # href enthält z.B. "PART_3/AD_2/PRI/AD_2_LOWW/LO_AD_2_LOWW_en.pdf"
        m = re.search(r'AD_2_([A-Z]{4})/', href)
        if m:
            icao = m.group(1)
            if icao not in codes:
                codes.append(icao)
    return codes


def karten_fuer_flughafen(icao, basis):
    """Ruft die airport-spezifische HTM-Seite auf und sammelt alle Karten-PDFs."""
    url = basis + f"ad_2_{icao.lower()}.htm"
    try:
        links = seite_laden(url, timeout=15)
    except Exception:
        return {}, url

    karten = {}
    for text, href in links:
        if not href.lower().endswith(".pdf") or not text:
            continue
        if not href.startswith("http"):
            href = basis + href
        karten[text] = href

    return karten, url


def durchlauf():
    print("Suche aktuelle Austrocontrol AIP-Ausgabe...")
    basis = aktuelle_edition_basis()
    print(f"  Basis: {basis}")

    print("Lade Flughafen-Liste (AD 2)...")
    codes = flughafen_icao_codes(basis)
    print(f"  {len(codes)} österreichische Flughäfen gefunden")

    katalog = {}
    for icao in codes:
        karten, ap_url = karten_fuer_flughafen(icao, basis)
        print(f"  {icao}: {len(karten)} Karten", flush=True)
        katalog[icao] = {"_url": ap_url, "karten": karten}

    pfad = os.path.join(REPO_DIR, AUSGABE)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"\nGespeichert: {AUSGABE} ({len(katalog)} Flughäfen)")

    git = r"C:\Program Files\Git\cmd\git.exe"
    subprocess.run([git, "-C", REPO_DIR, "add", AUSGABE], check=True)
    result = subprocess.run([git, "-C", REPO_DIR, "commit",
                             "-m", "Austrocontrol AIP (LO) automatisch aktualisiert"])
    if result.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen – kein Push nötig.")


def main():
    import sys
    if "--loop" in sys.argv:
        import time
        while True:
            print("Starte Durchlauf...")
            try:
                durchlauf()
            except Exception:
                import traceback; traceback.print_exc()
            print("Nächster Durchlauf in 6 Stunden.\n")
            time.sleep(6 * 60 * 60)
    else:
        durchlauf()


if __name__ == "__main__":
    main()
