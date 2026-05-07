"""
netherlands_bot.py – Scraper für LVNL eAIP (Niederlande / EH)
Kein Selenium – reines HTML. Aktuelle AIRAC wird automatisch erkannt.
Ausgabe: eh_katalog_export.json
"""

import re, json, os, requests
from datetime import date
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, unquote

REPO_DIR   = os.path.dirname(os.path.abspath(__file__))
DEFAULT_URL = 'https://eaip.lvnl.nl/web/eaip/default.html'
OUTPUT     = 'eh_katalog_export.json'

LABEL_RE = re.compile(r'^EH[A-Z]{2}-(.+?)(?:\.pdf)?$', re.I)

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                       '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Encoding': 'identity',
})


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


def get_text(url):
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text


def aktuellen_airac_finden():
    """Liest default.html und gibt die URL des aktuell gültigen AIRAC zurück."""
    html = get_text(DEFAULT_URL)
    today = date.today()
    best_date, best_path = None, None
    for href in re.findall(r'href=["\']([^"\']*AIRAC[^"\']+index\.html)["\']', html, re.I):
        m = re.search(r'(\d{4})_(\d{2})_(\d{2})', href)
        if not m:
            continue
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d <= today and (best_date is None or d > best_date):
            best_date, best_path = d, href
    if not best_path:
        raise RuntimeError('Kein gültiger AIRAC gefunden')
    clean = best_path.replace('\\', '/')
    base  = 'https://eaip.lvnl.nl/web/eaip/' + quote(clean.rsplit('index.html', 1)[0], safe='/')
    print(f'  AIRAC {best_date}: {base}')
    return base


def flughaefen_aus_menu(base):
    """Alle EH-Flughafen-ICAO-Codes aus dem Navigationsmenü."""
    menu_url = base + 'eAIP/menu.html'
    html = get_text(menu_url)
    codes = sorted(set(re.findall(r'\b(EH[A-Z]{2})\b', html)))
    return codes


def chart_label(href, text):
    t = text.strip()
    if t and len(t) > 1 and '://' not in t and not t.startswith('../') and len(t) < 80:
        return t
    fname = unquote(href.split('/')[-1].split('?')[0])
    fname = re.sub(r'\.pdf$', '', fname, flags=re.I)
    m = LABEL_RE.match(fname)
    return m.group(1) if m else fname


def karten_fuer_flughafen(icao, base):
    """Sammelt alle PDF-Links über alle Sektionen eines Flughafens."""
    eaip_base = base + 'eAIP/'
    karten = {}
    seen_urls = set()

    for n in range(1, 30):
        fname = quote(f'EH-AD 2 {icao} {n}-en-GB.html')
        url   = eaip_base + fname
        try:
            r = SESSION.get(url, timeout=10)
        except Exception:
            break
        if r.status_code == 404:
            break
        if r.status_code != 200:
            continue
        r.encoding = 'utf-8'
        p = LinkParser()
        p.feed(r.text)
        for text, href in p.links:
            if not href or '.pdf' not in href.lower():
                continue
            abs_url = urljoin(url, href.split('"')[0])
            if abs_url in seen_urls:
                continue
            seen_urls.add(abs_url)
            label = chart_label(href, text)
            if label and label not in karten:
                karten[label] = abs_url

    ap_url = eaip_base + quote(f'EH-AD 2 {icao} 1-en-GB.html')
    return karten, ap_url


def main():
    print(f'Suche aktuellen AIRAC: {DEFAULT_URL}')
    base = aktuellen_airac_finden()

    print('Lade Flughafen-Liste...')
    codes = flughaefen_aus_menu(base)
    print(f'{len(codes)} Flughäfen: {codes}')

    katalog = {}
    for icao in codes:
        karten, ap_url = karten_fuer_flughafen(icao, base)
        print(f'  {icao}: {len(karten)} Karten', flush=True)
        if karten:
            katalog[icao] = {'_url': ap_url, 'karten': karten}

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f'Gespeichert: {OUTPUT} ({len(katalog)} Flughäfen)')


if __name__ == '__main__':
    main()
