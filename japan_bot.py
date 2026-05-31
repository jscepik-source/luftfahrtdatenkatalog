"""
japan_bot.py – Scraper für JCAB AIP Japan via nagodede.github.io
Kein Selenium nötig – reines HTML mit direkten PDF-Links.
Ausgabe: rj_katalog_export.json  (deckt RJ* und RO* ab)
"""

import re, json, os, requests
from html.parser import HTMLParser

REPO_DIR   = os.path.dirname(os.path.abspath(__file__))
INDEX_URL  = "https://nagodede.github.io/aip/japan/"
BASE_URL   = "https://nagodede.github.io"
OUTPUT     = "rj_katalog_export.json"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; AIPBot/1.0)"})


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._buf  = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href", "")
            self._buf  = []

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append(("".join(self._buf).strip(), self._href))
            self._href = None

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)


def main():
    print(f"Lade Index: {INDEX_URL}")
    r = SESSION.get(INDEX_URL, timeout=30)
    r.raise_for_status()

    parser = LinkParser()
    parser.feed(r.text)

    katalog = {}
    for text, href in parser.links:
        m = re.search(r'/aip/japan/documents/([A-Z]{4})_(chart|full)\.pdf', href)
        if not m:
            continue
        icao = m.group(1)
        typ  = m.group(2)
        url  = BASE_URL + href if href.startswith("/") else href

        if icao not in katalog:
            katalog[icao] = {"_url": INDEX_URL, "karten": {}}

        label = "AIP Charts (PDF)" if typ == "chart" else "AIP Full Document (PDF)"
        katalog[icao]["karten"][label] = url

    print(f"{len(katalog)} Flughäfen gefunden (RJ* + RO*)")

    out = os.path.join(REPO_DIR, OUTPUT)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"Gespeichert: {OUTPUT}")


if __name__ == "__main__":
    main()
