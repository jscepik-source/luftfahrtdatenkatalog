"""
benelux_bot.py – Scraper für Benelux eAIPs
  EB – Belgien   (skeyes / ops.skeyes.be)
  EH – Niederlande (LVNL / eaip.lvnl.nl)
  EL – Luxemburg  (ANA / ana.lu)

Alle drei nutzen das EUROCONTROL-Standard-eAIP-Format:
  Flughafenseite: html/eAIP/{CC}-AD-2-{ICAO}-en-GB.html
"""

import re, json, os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
try:
    from webdriver_manager.chrome import ChromeDriverManager
    _mgr = True
except ImportError:
    _mgr = False

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

LAENDER = [
    {
        'prefix':    'EB',
        'name':      'skeyes eAIP Belgien',
        'portal':    'https://ops.skeyes.be/html/belgocontrol_static/eaip_upcoming/eAIP_Main/html/index-en-GB.html',
        'eaip_re':   re.compile(r'ops\.skeyes\.be.*index.*en-GB\.html', re.I),
        'fallback':  'https://ops.skeyes.be/html/belgocontrol_static/eaip_upcoming/eAIP_Main/html/index-en-GB.html',
        'output':    'eb_katalog_export.json',
    },
    {
        'prefix':    'EH',
        'name':      'LVNL eAIP Niederlande',
        'portal':    'https://www.lvnl.nl/diensten/aip',
        'eaip_re':   re.compile(r'eaip\.lvnl\.nl/web/.*AIRAC.*/html/index.*\.html', re.I),
        'fallback':  None,   # wird dynamisch aus dem Portal geholt
        'output':    'eh_katalog_export.json',
    },
    {
        'prefix':    'EL',
        'name':      'ANA eAIP Luxemburg',
        'portal':    'https://www.ana.lu/en/aeronautical-information/integrated-aeronautical-information-package',
        'eaip_re':   re.compile(r'ana\.lu.*index.*en.*\.html|ead.*EL.*index', re.I),
        'fallback':  None,
        'output':    'el_katalog_export.json',
    },
]

CHART_EXTS = {'.pdf', '.png', '.jpg', '.jpeg', '.svg'}
ICAO4_RE   = re.compile(r'\b([A-Z]{4})\b')
AP_PAGE_RE = re.compile(r'([A-Z]{2})-AD-2-([A-Z]{4})-en-GB\.html', re.I)
PDF_RE     = re.compile(r'\.pdf(\?.*)?$', re.I)


def make_browser():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--lang=en-US')
    if _mgr:
        svc = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=svc, options=opts)
    return webdriver.Chrome(options=opts)


def warte(br, sek=3, timeout=15):
    try:
        WebDriverWait(br, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a')))
    except Exception:
        pass
    time.sleep(sek)


def alle_links(br):
    return [(a.text.strip(), a.get_attribute('href') or '')
            for a in br.find_elements(By.TAG_NAME, 'a')]


def finde_eaip_index(br, land):
    """Öffnet Portal und sucht den Link zum aktuellen eAIP-Index."""
    print(f"  Öffne Portal: {land['portal']}")
    br.get(land['portal'])
    warte(br)

    for text, href in alle_links(br):
        if href and land['eaip_re'].search(href):
            print(f"  eAIP-Index gefunden: {href}")
            return href

    if land['fallback']:
        print(f"  Fallback: {land['fallback']}")
        return land['fallback']

    print(f"  WARNUNG: kein eAIP-Index gefunden für {land['prefix']}")
    return None


def finde_flughafen_urls(br, index_url, prefix):
    """Navigiert von eAIP-Index zur AD-2-Liste und sammelt Flughafen-URLs."""
    br.get(index_url)
    warte(br)

    base = index_url.rsplit('/html/', 1)[0] + '/html/'
    flughaefen = {}

    # Direkte Suche auf der Indexseite
    for text, href in alle_links(br):
        if not href:
            continue
        m = AP_PAGE_RE.search(href)
        if m and m.group(2).startswith(prefix):
            icao = m.group(2).upper()
            if icao not in flughaefen:
                flughaefen[icao] = href if href.startswith('http') else base + href.lstrip('/')

    if flughaefen:
        return flughaefen

    # Versuche AD-2-Navigationslink
    for text, href in alle_links(br):
        if href and re.search(r'AD.?2|Aerodrome|aerodromes', text, re.I):
            print(f"  AD-2-Link: {href}")
            br.get(href if href.startswith('http') else base + href.lstrip('/'))
            warte(br)
            for t2, h2 in alle_links(br):
                if not h2:
                    continue
                m = AP_PAGE_RE.search(h2)
                if m and m.group(2).upper().startswith(prefix):
                    icao = m.group(2).upper()
                    if icao not in flughaefen:
                        flughaefen[icao] = h2 if h2.startswith('http') else base + h2.lstrip('/')
            break

    return flughaefen


def scrape_flughafen(br, icao, url, base_domain):
    """Öffnet Flughafenseite und sammelt alle PDF-Chart-Links."""
    try:
        br.get(url)
        warte(br, sek=2, timeout=10)
    except Exception as e:
        print(f"    {icao}: Fehler beim Laden – {e}")
        return {}

    karten = {}
    for text, href in alle_links(br):
        if not href or not text:
            continue
        if PDF_RE.search(href) or any(href.lower().endswith(e) for e in CHART_EXTS):
            label = text.strip()
            if label and label not in karten:
                karten[label] = href
    return karten


def scrape_land(br, land):
    prefix = land['prefix']
    print(f"\n[{prefix}] {land['name']}")

    index_url = finde_eaip_index(br, land)
    if not index_url:
        return {}

    br.get(index_url)
    warte(br)

    base_domain = re.match(r'https?://[^/]+', index_url)
    base_domain = base_domain.group(0) if base_domain else ''

    flughaefen = finde_flughafen_urls(br, index_url, prefix)
    print(f"  {len(flughaefen)} Flughäfen gefunden: {list(flughaefen.keys())}")

    katalog = {}
    for icao, fh_url in flughaefen.items():
        karten = scrape_flughafen(br, icao, fh_url, base_domain)
        print(f"  {icao}: {len(karten)} Karten", flush=True)
        katalog[icao] = {'_url': fh_url, 'karten': karten}

    return katalog


def main():
    import sys
    nur = sys.argv[1].upper() if len(sys.argv) > 1 else None

    br = make_browser()
    try:
        for land in LAENDER:
            if nur and land['prefix'] != nur:
                continue
            katalog = scrape_land(br, land)
            if not katalog:
                print(f"  [{land['prefix']}] Leer – übersprungen")
                continue
            pfad = os.path.join(REPO_DIR, land['output'])
            with open(pfad, 'w', encoding='utf-8') as f:
                json.dump(katalog, f, indent=2, ensure_ascii=False)
            print(f"  Gespeichert: {land['output']} ({len(katalog)} Flughäfen)")
    finally:
        br.quit()


if __name__ == '__main__':
    main()
