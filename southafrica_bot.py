"""
southafrica_bot.py – Scraper für SACAA-Karten (Südafrika / FA)
Kein Selenium nötig – direkte PDF-Links auf Azure Blob Storage.
Ausgabe: fa_katalog_export.json
"""

import re, json, os, requests
from html.parser import HTMLParser
from urllib.parse import unquote

REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
INDEX_URL = "https://www.caa.co.za/industry-information/aeronautical-information-aeronautical-charts/"
BLOB_HOST = "https://caasanwebsitestorage.blob.core.windows.net"
OUTPUT    = "fa_katalog_export.json"

ICAO_RE = re.compile(r'^(FA[A-Z]{2})\b', re.IGNORECASE)

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


def chart_label(href, link_text):
    """Erzeuge einen lesbaren Kartennamen aus Link-Text oder Dateiname."""
    if link_text:
        return link_text.strip()
    filename = unquote(href.split("/")[-1])
    filename = re.sub(r'\.pdf$', '', filename, flags=re.IGNORECASE)
    m = ICAO_RE.match(filename)
    if m:
        filename = filename[len(m.group(1)):].lstrip('_- ')
    return filename or href


def main():
    print(f"Lade SACAA-Seite: {INDEX_URL}")
    r = SESSION.get(INDEX_URL, timeout=30)
    r.raise_for_status()

    parser = LinkParser()
    parser.feed(r.text)

    katalog = {}
    for text, href in parser.links:
        if not href:
            continue
        # Nur Azure-Blob-PDFs
        if BLOB_HOST not in href and "aeronautical-charts" not in href:
            continue
        if not href.lower().endswith(".pdf"):
            continue

        # Absolute URL sicherstellen
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://caasanwebsitestorage.blob.core.windows.net" + href

        filename = unquote(href.split("/")[-1])
        m = ICAO_RE.match(filename.upper())
        if not m:
            continue
        icao = m.group(1).upper()

        if icao not in katalog:
            katalog[icao] = {"_url": INDEX_URL, "karten": {}}

        label = chart_label(href, text)
        # Doppelte Labels vermeiden
        if label in katalog[icao]["karten"]:
            label = f"{label} ({len(katalog[icao]['karten'])+1})"
        katalog[icao]["karten"][label] = href

    print(f"{len(katalog)} Flughäfen gefunden (FA*)")

    out = os.path.join(REPO_DIR, OUTPUT)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"Gespeichert: {OUTPUT}")


if __name__ == "__main__":
    main()
