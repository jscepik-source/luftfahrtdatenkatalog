"""
eaip_bot.py – Generischer Scraper für EUROCONTROL-Standard-eAIPs.
Jedes Land wird als eigene JSON gespeichert: lo_katalog_export.json usw.
"""

import re, json, time, os, subprocess
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

# ── Länderkonfigurationen ───────────────────────────────────────────────────
# Jeder Eintrag:
#   prefix     – ICAO-Länderpräfix (2 Buchstaben)
#   name       – Anzeigename
#   start_url  – AIP-Startseite oder direkte eAIP-Root
#   ad2_text   – Text des Links, der zur AD-2-Seite führt  (für nav_selenium)
#   mode       – 'selenium' (Standard) oder 'static' (fixes URL-Muster)
#   static_ad2 – direkte URL der Flughafenliste (nur mode=static)
#   static_ap  – URL-Template mit {icao} für einzelne Flughäfen (nur mode=static)
#   pdf_host   – Host-Präfix für relative PDF-Links (nur mode=static)
#   output     – Ausgabedateiname
# ---------------------------------------------------------------------------
LAND_KONFIGS = [
    # ── Europa ──────────────────────────────────────────────────────────────
    {
        'prefix':   'LO',
        'name':     'Austrocontrol AIP (Österreich)',
        'start_url':'https://eaip.austrocontrol.at/',
        'mode':     'selenium',
        'output':   'lo_katalog_export.json',
    },
    {
        'prefix':   'LS',
        'name':     'Skybriefing AIP (Schweiz)',
        'start_url':'https://www.skybriefing.com/',
        'mode':     'selenium',
        'output':   'ls_katalog_export.json',
    },
    {
        'prefix':   'LK',
        'name':     'ŘLP AIP (Tschechien)',
        'start_url':'https://aim.rlp.cz/',
        'mode':     'selenium',
        'output':   'lk_katalog_export.json',
    },
    {
        'prefix':   'LZ',
        'name':     'LPS SR AIP (Slowakei)',
        'start_url':'https://lps.sk/en/index.php/aeronautical-information-services/aip',
        'mode':     'selenium',
        'output':   'lz_katalog_export.json',
    },
    {
        'prefix':   'LH',
        'name':     'HungaroControl AIP (Ungarn)',
        'start_url':'https://www.hungarocontrol.hu/aip/',
        'mode':     'selenium',
        'output':   'lh_katalog_export.json',
    },
    {
        'prefix':   'LR',
        'name':     'ROMATSA AIP (Rumänien)',
        'start_url':'https://www.romatsa.ro/en/aip',
        'mode':     'selenium',
        'output':   'lr_katalog_export.json',
    },
    {
        'prefix':   'LB',
        'name':     'BULATSA AIP (Bulgarien)',
        'start_url':'https://www.bulatsa.com/en/aip',
        'mode':     'selenium',
        'output':   'lb_katalog_export.json',
    },
    {
        'prefix':   'LJ',
        'name':     'Sloveniacontrol AIP (Slowenien)',
        'start_url':'https://www.sloveniacontrol.si/acrobat/aip/info/index.html',
        'mode':     'selenium',
        'output':   'lj_katalog_export.json',
    },
    {
        'prefix':   'LD',
        'name':     'Croatia Control AIP (Kroatien)',
        'start_url':'https://www.crocontrol.hr/en/aip',
        'mode':     'selenium',
        'output':   'ld_katalog_export.json',
    },
    {
        'prefix':   'LI',
        'name':     'ENAV AIP (Italien)',
        'start_url':'https://www.enav.it/sites/public/en/aeronautical-services/publications/aip.html',
        'mode':     'selenium',
        'output':   'li_katalog_export.json',
    },
    {
        'prefix':   'LE',
        'name':     'ENAIRE AIP (Spanien)',
        'start_url':'https://ais.enaire.es/AIP/AIP_VIG/aip/indexEN.html',
        'mode':     'selenium',
        'output':   'le_katalog_export.json',
    },
    {
        'prefix':   'LP',
        'name':     'NAV Portugal AIP',
        'start_url':'https://www.nav.pt/en/aeronautical-information',
        'mode':     'selenium',
        'output':   'lp_katalog_export.json',
    },
    {
        'prefix':   'LG',
        'name':     'HCAA AIP (Griechenland)',
        'start_url':'https://www.hcaa.gr/en/aeronautical-information',
        'mode':     'selenium',
        'output':   'lg_katalog_export.json',
    },
    {
        'prefix':   'LT',
        'name':     'DHMI AIP (Türkei)',
        'start_url':'https://aip.dhmi.gov.tr/',
        'mode':     'selenium',
        'output':   'lt_katalog_export.json',
    },
    {
        'prefix':   'LF',
        'name':     'SIA/DSNA AIP (Frankreich)',
        'start_url':'https://www.sia.aviation-civile.gouv.fr/en/publications/aip-france-from-the-online-store.html',
        'mode':     'selenium',
        'output':   'lf_katalog_export.json',
    },
    {
        'prefix':   'EG',
        'name':     'NATS AIP (Großbritannien)',
        'start_url':'https://nats-uk.ead-it.com/cms-nats/opencms/en/Publications/AIP/',
        'mode':     'selenium',
        'output':   'eg_katalog_export.json',
    },
    {
        'prefix':   'EI',
        'name':     'IAA AIP (Irland)',
        'start_url':'https://www.iaa.ie/commercial-aviation/aeronautical-information-infrastructure-aai/publications',
        'mode':     'selenium',
        'output':   'ei_katalog_export.json',
    },
    {
        'prefix':   'EK',
        'name':     'Naviair AIP (Dänemark)',
        'start_url':'https://aim.naviair.dk/',
        'mode':     'selenium',
        'output':   'ek_katalog_export.json',
    },
    {
        'prefix':   'EF',
        'name':     'Finavia AIP (Finnland)',
        'start_url':'https://www.ais.fi/en/',
        'mode':     'selenium',
        'output':   'ef_katalog_export.json',
    },
    {
        'prefix':   'ES',
        'name':     'LFV AIP (Schweden)',
        'start_url':'https://aro.lfv.se/',  # AIP nur über EAD-Login – scraping limitiert
        'mode':     'selenium',
        'output':   'es_katalog_export.json',
    },
    {
        'prefix':   'EN',
        'name':     'Avinor AIP (Norwegen)',
        'start_url':'https://avinor.no/en/ais/',
        'mode':     'selenium',
        'output':   'en_katalog_export.json',
    },
    {
        'prefix':   'EB',
        'name':     'skeyes AIP (Belgien)',
        'start_url':'https://ops.skeyes.be/html/belgocontrol_static/eaip_upcoming/eAIP_Main/html/index-en-GB.html',
        'mode':     'selenium',
        'output':   'eb_katalog_export.json',
    },
    {
        'prefix':   'EH',
        'name':     'LVNL AIP (Niederlande)',
        'start_url':'https://www.lvnl.nl/diensten/aip',
        'mode':     'selenium',
        'output':   'eh_katalog_export.json',
    },
    {
        'prefix':   'EP',
        'name':     'PANSA AIP (Polen)',
        'start_url':'https://www.ais.pansa.pl/aip/',
        'mode':     'selenium',
        'output':   'ep_katalog_export.json',
    },
    {
        'prefix':   'EE',
        'name':     'EANS AIP (Estland)',
        'start_url':'https://aim.eans.ee/',
        'mode':     'selenium',
        'output':   'ee_katalog_export.json',
    },
    {
        'prefix':   'EV',
        'name':     'LGS AIP (Lettland)',
        'start_url':'https://ais.lgs.lv/',
        'mode':     'selenium',
        'output':   'ev_katalog_export.json',
    },
    {
        'prefix':   'EY',
        'name':     'Oro navigacija AIP (Litauen)',
        'start_url':'https://www.ans.lt/en/aeronautical-information',
        'mode':     'selenium',
        'output':   'ey_katalog_export.json',
    },
    {
        'prefix':   'BI',
        'name':     'ISAVIA AIP (Island)',
        'start_url':'https://www.isavia.is/en/civil-aviation/aeronautical-information',
        'mode':     'selenium',
        'output':   'bi_katalog_export.json',
    },
    # ── Weitere Europa ──────────────────────────────────────────────────────
    {
        'prefix':   'LA',
        'name':     'Albcontrol AIP (Albanien)',
        'start_url':'http://www.albcontrol.al/',
        'mode':     'selenium',
        'output':   'la_katalog_export.json',
    },
    {
        'prefix':   'UD',
        'name':     'ArmATS AIP (Armenien)',
        'start_url':'http://www.armats.am/',
        'mode':     'selenium',
        'output':   'ud_katalog_export.json',
    },
    {
        'prefix':   'LQ',
        'name':     'BHDCA AIP (Bosnien & Herzegowina)',
        'start_url':'https://www.bhdca.gov.ba/',
        'mode':     'selenium',
        'output':   'lq_katalog_export.json',
    },
    {
        'prefix':   'LU',
        'name':     'MoldATSA AIP (Moldawien)',
        'start_url':'https://www.moldatsa.md/',
        'mode':     'selenium',
        'output':   'lu_katalog_export.json',
    },
    {
        'prefix':   'LY',
        'name':     'SMATSA AIP (Serbien/Montenegro)',
        'start_url':'https://smatsa.rs/',
        'mode':     'selenium',
        'output':   'ly_katalog_export.json',
    },
    # ── Naher Osten ─────────────────────────────────────────────────────────
    {
        'prefix':   'OM',
        'name':     'GCAA AIP (VAE)',
        'start_url':'https://www.gcaa.gov.ae/en/ais/pages/aip.aspx',
        'mode':     'selenium',
        'output':   'om_katalog_export.json',
    },
    {
        'prefix':   'OJ',
        'name':     'CARC AIP (Jordanien)',
        'start_url':'https://www.carc.gov.jo/en/Pages/default.aspx',
        'mode':     'selenium',
        'output':   'oj_katalog_export.json',
    },
    {
        'prefix':   'OB',
        'name':     'MOCI AIP (Bahrain)',
        'start_url':'https://www.mtt.gov.bh/',
        'mode':     'selenium',
        'output':   'ob_katalog_export.json',
    },
    {
        'prefix':   'LL',
        'name':     'CAAI AIP (Israel)',
        'start_url':'https://www.caa.gov.il/',
        'mode':     'selenium',
        'output':   'll_katalog_export.json',
    },
    {
        'prefix':   'OT',
        'name':     'QAA AIP (Katar)',
        'start_url':'https://aim.qatarairports.com/',
        'mode':     'selenium',
        'output':   'ot_katalog_export.json',
    },
    {
        'prefix':   'OO',
        'name':     'CAA AIP (Oman)',
        'start_url':'https://www.caa.gov.om/',
        'mode':     'selenium',
        'output':   'oo_katalog_export.json',
    },
    {
        'prefix':   'OE',
        'name':     'GACA eAIS (Saudi-Arabien)',
        'start_url':'https://eais.gaca.gov.sa/',
        'mode':     'selenium',
        'output':   'oe_katalog_export.json',
    },
    {
        'prefix':   'HE',
        'name':     'NANSC AIP (Ägypten)',
        'start_url':'http://www.nanscegypt.net/',
        'mode':     'selenium',
        'output':   'he_katalog_export.json',
    },
    # ── Afrika ──────────────────────────────────────────────────────────────
    {
        # ASECNA: 17 afrikanische Staaten – alle Präfixe in einer JSON
        'prefix':   ['DB','DF','DI','DR','DX','FC','FE','FG','FI','FK','FM','FO','FT','GA','GG','GO','GQ'],
        'name':     'ASECNA AIP (17 afrikanische Staaten)',
        'start_url':'https://aim.asecna.aero/',
        'mode':     'selenium',
        'output':   'asecna_katalog_export.json',
    },
    {
        'prefix':   'HK',
        'name':     'KCAA eAIP (Kenia)',
        'start_url':'https://eaip.kcaa.or.ke/',
        'mode':     'selenium',
        'output':   'hk_katalog_export.json',
    },
    {
        'prefix':   'GM',
        'name':     'ONDA AIP (Marokko)',
        'start_url':'https://www.onda.ma/',
        'mode':     'selenium',
        'output':   'gm_katalog_export.json',
    },
    {
        'prefix':   'FA',
        'name':     'CAA AIP (Südafrika)',
        'start_url':'https://www.caa.co.za/industry-information/aeronautical-information-aeronautical-charts/',
        'mode':     'selenium',
        'output':   'fa_katalog_export.json',
    },
    # ── Asien-Pazifik ───────────────────────────────────────────────────────
    # Japan → japan_bot.py (nagodede.github.io mirror, kein Selenium nötig)
    {
        'prefix':   'RK',
        'name':     'MOLIT AIP (Südkorea)',
        'start_url':'https://ais.koca.go.kr/',
        'mode':     'selenium',
        'output':   'rk_katalog_export.json',
    },
    {
        'prefix':   'WS',
        'name':     'CAAS AIP (Singapur)',
        'start_url':'https://aim-sg.caas.gov.sg/',
        'mode':     'selenium',
        'output':   'ws_katalog_export.json',
    },
    {
        'prefix':   'VT',
        'name':     'CAAT AIP (Thailand)',
        'start_url':'https://aip.caat.or.th/',
        'mode':     'selenium',
        'output':   'vt_katalog_export.json',
    },
    {
        'prefix':   'VH',
        'name':     'CAD AIP (Hongkong)',
        'start_url':'https://www.hkatc.gov.hk/',
        'mode':     'selenium',
        'output':   'vh_katalog_export.json',
    },
    {
        'prefix':   'VI',
        'name':     'AAI AIP (Indien)',
        'start_url':'https://aim-india.aai.aero/',
        'mode':     'selenium',
        'output':   'vi_katalog_export.json',
    },
    {
        'prefix':   'WI',
        'name':     'AirNav AIP (Indonesien)',
        'start_url':'https://navigasi-penerbangan.dephub.go.id/',
        'mode':     'selenium',
        'output':   'wi_katalog_export.json',
    },
    {
        'prefix':   'WM',
        'name':     'CAAM AIP (Malaysia)',
        'start_url':'https://aip.caam.gov.my/',
        'mode':     'selenium',
        'output':   'wm_katalog_export.json',
    },
    {
        'prefix':   'RP',
        'name':     'CAAP AIP (Philippinen)',
        'start_url':'https://caap.gov.ph/',
        'mode':     'selenium',
        'output':   'rp_katalog_export.json',
    },
    {
        'prefix':   'VC',
        'name':     'AASL AIP (Sri Lanka)',
        'start_url':'https://www.airport.lk/',
        'mode':     'selenium',
        'output':   'vc_katalog_export.json',
    },
    {
        'prefix':   'RC',
        'name':     'CAA eAIP (Taiwan)',
        'start_url':'https://eaip.caa.gov.tw/',
        'mode':     'selenium',
        'output':   'rc_katalog_export.json',
    },
    {
        'prefix':   'VV',
        'name':     'VNAISC AIP (Vietnam)',
        'start_url':'https://vnaic.vn/',
        'mode':     'selenium',
        'output':   'vv_katalog_export.json',
    },
    {
        'prefix':   'VM',
        'name':     'AACM AIP (Macau)',
        'start_url':'https://www.aacm.gov.mo/',
        'mode':     'selenium',
        'output':   'vm_katalog_export.json',
    },
    {
        'prefix':   'ZB',
        'name':     'CAAC AIP (China)',
        'start_url':'http://www.china-ais.org.cn/',
        'mode':     'selenium',
        'output':   'zb_katalog_export.json',
    },
    # ── Amerika ─────────────────────────────────────────────────────────────
    # USA → faa_bot.py
    {
        'prefix':   'C',
        'name':     'NAV CANADA AIP',
        'start_url':'https://www.navcanada.ca/en/aeronautical-information/aip-canada.aspx',
        'mode':     'selenium',
        'output':   'c_katalog_export.json',
    },
    {
        'prefix':   'SA',
        'name':     'EANA AIP (Argentinien)',
        'start_url':'https://ais.eana.com.ar/',
        'mode':     'selenium',
        'output':   'sa_katalog_export.json',
    },
    {
        'prefix':   'SB',
        'name':     'DECEA AIP (Brasilien)',
        'start_url':'https://aisweb.decea.mil.br/',
        'mode':     'selenium',
        'output':   'sb_katalog_export.json',
    },
    {
        'prefix':   'SC',
        'name':     'DGAC AIP (Chile)',
        'start_url':'https://www.aipchile.gob.cl/',
        'mode':     'selenium',
        'output':   'sc_katalog_export.json',
    },
    {
        'prefix':   'SE',
        'name':     'DGAC AIP (Ecuador)',
        'start_url':'https://www.aviacioncivil.gob.ec/',
        'mode':     'selenium',
        'output':   'se_katalog_export.json',
    },
    {
        'prefix':   'SK',
        'name':     'Aerocivil AIP (Kolumbien)',
        'start_url':'https://www.aerocivil.gov.co/',
        'mode':     'selenium',
        'output':   'sk_katalog_export.json',
    },
    # Kuba → cuba_bot.py (statisch, kein Selenium nötig)
    {
        'prefix':   'MM',
        'name':     'SENEAM AIP (Mexiko)',
        'start_url':'https://www.gob.mx/seneam',
        'mode':     'selenium',
        'output':   'mm_katalog_export.json',
    },
    {
        'prefix':   'SP',
        'name':     'CORPAC AIP (Peru)',
        'start_url':'https://www.corpac.gob.pe/',
        'mode':     'selenium',
        'output':   'sp_katalog_export.json',
    },
    {
        'prefix':   'SU',
        'name':     'DINACIA AIP (Uruguay)',
        'start_url':'https://www.dinacia.gub.uy/',
        'mode':     'selenium',
        'output':   'su_katalog_export.json',
    },
    {
        'prefix':   'SV',
        'name':     'INAC AIP (Venezuela)',
        'start_url':'http://www.inac.gob.ve/',
        'mode':     'selenium',
        'output':   'sv_katalog_export.json',
    },
    # ── Australien/NZ ───────────────────────────────────────────────────────
    {
        'prefix':   'Y',
        'name':     'Airservices Australia AIP',
        'start_url':'https://www.airservicesaustralia.com/aip/current/aip.asp',
        'mode':     'selenium',
        'output':   'y_katalog_export.json',
    },
    {
        'prefix':   'NZ',
        'name':     'Airways AIP (Neuseeland)',
        'start_url':'https://www.aip.net.nz/',
        'mode':     'selenium',
        'output':   'nz_katalog_export.json',
    },
]


# ── Selenium Hilfsroutinen ──────────────────────────────────────────────────

def make_browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US")
    if _mgr:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    return webdriver.Chrome(options=options)


def warte(browser, timeout=12):
    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )
    except Exception:
        pass
    time.sleep(2)


def alle_links(browser):
    return [(l.text.strip(), l.get_attribute('href'))
            for l in browser.find_elements(By.TAG_NAME, 'a')]


# ── Generischer eAIP-Scraper (Selenium) ─────────────────────────────────────

CHART_EXTS = {'.pdf', '.png', '.jpg', '.jpeg', '.svg', '.tiff', '.tif'}

CHART_SCHLUESSEL = re.compile(
    r'(chart|karte|approach|ILS|RNP|VOR|NDB|SID|STAR|LOC|IAP|DP|RNAV|APP|'
    r'runway|taxiway|diagram|terrain|obstacle|visual|arrival|departure|plate)',
    re.IGNORECASE
)

NAV_RE = re.compile(r'^[A-Z](-[A-Z])?$')

ICAO_RE = re.compile(r'\b([A-Z]{4})\b')


def ist_chart_link(text, href, ap_url, domain):
    if not text or not href:
        return False
    if href == ap_url:
        return False
    if any(x in href for x in ['javascript:', '#popup', 'mailto:']):
        return False
    ext = os.path.splitext(href.lower())[1]
    if ext in CHART_EXTS:
        return True
    if domain and domain not in href and href.startswith('http'):
        return False
    if CHART_SCHLUESSEL.search(text):
        return True
    return False


def ist_flughafen_link(text, href, prefix):
    if not text or not href:
        return False
    if any(x in href for x in ['javascript:', '#popup', 'mailto:']):
        return False
    m = ICAO_RE.search(text + ' ' + (href or ''))
    if not m:
        return False
    code = m.group(1)
    # prefix kann ein String oder eine Liste sein
    prefixes = prefix if isinstance(prefix, (list, tuple)) else [prefix]
    if not any(code.startswith(p) for p in prefixes):
        return False
    if NAV_RE.match(text.strip()):
        return False
    return True


def extrahiere_domain(url):
    try:
        from urllib.parse import urlparse
        p = urlparse(url)
        return p.scheme + '://' + p.netloc
    except Exception:
        return ''


def finde_ad2_url(browser, prefix):
    """Versucht, die AD-2-Seite aus der aktuellen Navigation zu finden."""
    kandidaten = [
        'AD 2', 'AD-2', 'Aerodromes', 'AD Aerodromes',
        'Aerodrome', f'AD 2 {prefix}', 'Part 2',
    ]
    links = alle_links(browser)
    for suchtext in kandidaten:
        for text, href in links:
            if suchtext.lower() in text.lower() and href:
                return href
    # Versuche ICAO-Codes direkt zu finden (mancher eAIP bietet direkte Liste)
    for text, href in links:
        if href and re.search(rf'{prefix}[A-Z]{{2}}', text) and len(text) > 4:
            return None  # Flughäfen sind bereits sichtbar – kein AD-2-Klick nötig
    return None


def scrape_land_selenium(browser, konfig):
    prefix = konfig['prefix']  # str oder list
    prefix_str = prefix[0] if isinstance(prefix, (list, tuple)) else prefix
    start  = konfig['start_url']
    domain = extrahiere_domain(start)
    katalog = {}

    print(f"    → {start}")
    browser.get(start)
    warte(browser)

    # ── Schritt 1: AD 2 finden und navigieren ─────────────────────
    ad2_url = finde_ad2_url(browser, prefix_str)
    if ad2_url:
        print(f"    AD-2: {ad2_url}")
        browser.get(ad2_url)
        warte(browser)

    # ── Schritt 2: Flughäfen sammeln ──────────────────────────────
    flughafen_urls = {}
    for text, href in alle_links(browser):
        if ist_flughafen_link(text, href, prefix):
            m = ICAO_RE.search(text + ' ' + (href or ''))
            if m:
                icao = m.group(1)
                if icao not in flughafen_urls:
                    flughafen_urls[icao] = href

    print(f"    Gefunden: {len(flughafen_urls)} Flughäfen")

    # ── Schritt 3: Karten je Flughafen ────────────────────────────
    for icao, fh_url in flughafen_urls.items():
        try:
            browser.get(fh_url)
            warte(browser, timeout=8)

            karten = {}
            for text, href in alle_links(browser):
                if ist_chart_link(text, href, fh_url, domain) and text:
                    karten[text.strip()] = href

            print(f"    {icao}: {len(karten)} Karten", flush=True)
            katalog[icao] = {'_url': fh_url, 'karten': karten}
        except Exception as ex:
            print(f"    {icao}: Fehler – {ex}")

    return katalog


# ── Hauptschleife ────────────────────────────────────────────────────────────

def scrape_alle(nur_prefix=None):
    browser = make_browser()
    ergebnisse = {}
    try:
        for konfig in LAND_KONFIGS:
            prefix = konfig['prefix']
            if nur_prefix:
                if isinstance(prefix, (list, tuple)):
                    if nur_prefix not in prefix:
                        continue
                elif prefix != nur_prefix:
                    continue
            print(f"\n[{prefix}] {konfig['name']}")
            try:
                katalog = scrape_land_selenium(browser, konfig)
                ergebnisse[prefix] = (katalog, konfig['output'])
                print(f"  → {len(katalog)} Flughäfen")
            except Exception as e:
                import traceback
                print(f"  Fehler: {e}")
                traceback.print_exc()
    finally:
        browser.quit()
    return ergebnisse


def speichern_und_push(ergebnisse):
    geaendert = []
    for prefix, (katalog, dateiname) in ergebnisse.items():
        if not katalog:
            print(f"[{prefix}] Leer – wird übersprungen")
            continue
        pfad = os.path.join(REPO_DIR, dateiname)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(katalog, f, indent=2, ensure_ascii=False)
        geaendert.append(dateiname)
        print(f"[{prefix}] Gespeichert: {dateiname} ({len(katalog)} Flughäfen)")

    if not geaendert:
        print("Keine Änderungen.")
        return

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, '-C', REPO_DIR, 'add'] + geaendert, check=True)
    result = subprocess.run([git, '-C', REPO_DIR, 'commit',
                             '-m', 'eAIP-Karten automatisch aktualisiert'])
    if result.returncode == 0:
        subprocess.run([git, '-C', REPO_DIR, 'push'], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine neuen Änderungen.")


def main():
    import sys
    nur = sys.argv[1].upper() if len(sys.argv) > 1 else None
    ergebnisse = scrape_alle(nur_prefix=nur)
    speichern_und_push(ergebnisse)


if __name__ == '__main__':
    main()
