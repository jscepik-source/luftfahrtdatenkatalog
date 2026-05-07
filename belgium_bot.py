"""
belgium_bot.py – Scraper für skeyes eAIP (Belgien EB + Luxemburg EL)
Kein Selenium nötig – reines HTML mit direkten PDF-Links.
Ausgabe: eb_katalog_export.json, el_katalog_export.json
"""

import re, json, os, requests
from html.parser import HTMLParser
from urllib.parse import urljoin, unquote

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

BASE     = 'https://ops.skeyes.be/html/belgocontrol_static/eaip_upcoming/eAIP_Main/html/'
EAIP     = BASE + 'eAIP/'
INDEX    = BASE + 'index-en-GB.html'
MENU     = EAIP + 'EB-menu-en-GB.html'

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Encoding': 'identity',
    'Referer':         INDEX,
})

ICAO4_RE  = re.compile(r'\b([A-Z]{4})\b')
LABEL_RE  = re.compile(r'^[A-Z]{4}_(.+?)(?:_v\d+)?\.pdf$', re.I)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._buf  = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self._href = dict(attrs).get('href', '') or ''
            self._buf  = []

    def handle_endtag(self, tag):
        if tag == 'a' and self._href is not None:
            self.links.append((''.join(self._buf).strip(), self._href))
            self._href = None

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)


def get_links(url):
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    r.encoding = 'utf-8'
    p = LinkParser()
    p.feed(r.text)
    return p.links


def chart_label(href, text):
    """Lesbarer Kartenname aus Linktext oder Dateiname."""
    t = text.strip()
    if t and len(t) > 2 and not t.startswith('../'):
        return t
    fname = unquote(href.split('/')[-1].split('?')[0])
    m = LABEL_RE.match(fname)
    return m.group(1).replace('_', ' ') if m else fname


def flughaefen_aus_menu():
    """Alle ICAO-Codes aus dem skeyes-Navigationsmenü."""
    links = get_links(MENU)
    codes = []
    seen  = set()
    for _, href in links:
        m = re.search(r'EB-AD-2\.([A-Z]{4})-en-GB\.html', href)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            codes.append(m.group(1))
    return codes


def karten_fuer_flughafen(icao):
    """PDF-Links von der Flughafenseite."""
    url = EAIP + f'EB-AD-2.{icao}-en-GB.html'
    try:
        links = get_links(url)
    except Exception as e:
        print(f'  {icao}: Fehler – {e}')
        return {}, url

    karten = {}
    for text, href in links:
        if not href or '.pdf' not in href.lower():
            continue
        abs_url = urljoin(url, href.split('"')[0])  # Anführungszeichen abschneiden
        label = chart_label(href, text)
        if label and label not in karten:
            karten[label] = abs_url
    return karten, url


def main():
    print(f'Lade Menü: {MENU}')
    codes = flughaefen_aus_menu()
    print(f'{len(codes)} Flughäfen (EB* + EL*): {codes}')

    eb_katalog = {}
    el_katalog = {}

    for icao in codes:
        karten, ap_url = karten_fuer_flughafen(icao)
        print(f'  {icao}: {len(karten)} Karten', flush=True)
        eintrag = {'_url': ap_url, 'karten': karten}
        if icao.startswith('EL'):
            el_katalog[icao] = eintrag
        else:
            eb_katalog[icao] = eintrag

    for katalog, datei in [(eb_katalog, 'eb_katalog_export.json'),
                           (el_katalog, 'el_katalog_export.json')]:
        if not katalog:
            continue
        pfad = os.path.join(REPO_DIR, datei)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(katalog, f, indent=2, ensure_ascii=False)
        print(f'Gespeichert: {datei} ({len(katalog)} Flughäfen)')


if __name__ == '__main__':
    main()
