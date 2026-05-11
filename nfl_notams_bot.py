from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re
import os
import requests
import subprocess
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

AIP_URL = "https://aip.dfs.de/BasicAIP/"
NFL_FALLBACK_URL = "https://nfl.dfs.de/basic/scripts/stub/startApplication.php"
PAGE_SIZE = 400


def warte(browser, timeout=15):
    WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    time.sleep(4)


def dhxr_entfernen(url):
    return re.sub(r'[?&]dhxr\d+=\d+', '', url).rstrip('?&')


def iframe_urls(browser):
    return [dhxr_entfernen(f.get_attribute('src') or '')
            for f in browser.find_elements(By.TAG_NAME, 'iframe') if f.get_attribute('src')]


def connector_url_bauen(base_url, pos_start, count):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop('dhxr', None)
    for k in list(params.keys()):
        if k.startswith('dhxr'):
            del params[k]
    params['posStart'] = [str(pos_start)]
    params['count'] = [str(count)]
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse(parsed._replace(query=new_query))


def xml_parsen(xml_text):
    import xml.etree.ElementTree as ET
    eintraege = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"    XML-Fehler: {e}")
        return eintraege
    for row in root.findall('row'):
        cells = [c.text or '' for c in row.findall('cell')]
        nummer = cells[2].strip() if len(cells) > 2 else ''
        teil   = cells[1].strip() if len(cells) > 1 else ''
        if nummer:
            eintraege.append({'nummer': nummer, 'teil': teil})
    return eintraege


def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    export = {'eintraege': []}

    try:
        print("1. BasicAIP laden...")
        browser.get(AIP_URL)
        warte(browser)

        nfl_url = next((el.get_attribute('href') for el in browser.find_elements(By.TAG_NAME, 'a')
                        if "Nachrichten" in el.text and "Luftfahrer" in el.text
                        and el.get_attribute('href')), NFL_FALLBACK_URL)

        print("2. NfL-Startseite...")
        browser.get(nfl_url)
        warte(browser)
        pane_url = next((u for u in iframe_urls(browser) if 'showPaneSet' in u), None)

        print("3. Pane laden...")
        browser.get(pane_url)
        warte(browser)
        grid_url = next((u for u in iframe_urls(browser) if 'showGrid' in u), None)

        print("4. Grid laden...")
        browser.get(grid_url)
        time.sleep(6)

        ajax_urls = browser.execute_script("""
            return performance.getEntriesByType('resource')
                .map(e => e.name)
                .filter(u => u.includes('connGrid') || u.includes('connector'));
        """)

        connector_url = next((u for u in ajax_urls if 'connGrid' in u or 'connector' in u), None)
        if not connector_url:
            raise RuntimeError("Keine Connector-URL gefunden")

        total = browser.execute_script("return globalActiveDHTMLGridObject.getRowsNum();")
        print(f"Gesamt: {total} NfL-Einträge")

        cookies = {c['name']: c['value'] for c in browser.get_cookies()}
        session = requests.Session()
        session.cookies.update(cookies)
        session.headers.update({'Referer': grid_url, 'User-Agent': 'Mozilla/5.0'})

        base_url = dhxr_entfernen(connector_url)
        alle_eintraege = []

        for start in range(0, total, PAGE_SIZE):
            url = connector_url_bauen(base_url, start, PAGE_SIZE)
            r = session.get(url, timeout=30)
            zeilen = xml_parsen(r.text)
            alle_eintraege.extend(zeilen)
            print(f"  {start}–{min(start+PAGE_SIZE, total)}: {len(zeilen)} Einträge")

        # Deduplizieren
        seen = set()
        unique = []
        for e in alle_eintraege:
            if e['nummer'] not in seen:
                seen.add(e['nummer'])
                unique.append(e)

        export['eintraege'] = unique
        print(f"{len(unique)} NfL-Einträge gespeichert.")

        out_path = os.path.join(REPO_DIR, "nfl_notams_export.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)

        print("JSON gespeichert.")

        _win_git = r"C:\Program Files\Git\cmd\git.exe"
        git = _win_git if os.path.isfile(_win_git) else "git"
        subprocess.run([git, "-C", REPO_DIR, "add", "nfl_notams_export.json"], check=True)
        result = subprocess.run([git, "-C", REPO_DIR, "commit", "-m", "NfL-NOTAMs automatisch aktualisiert"])
        if result.returncode == 0:
            subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
            print("GitHub aktualisiert.")
        else:
            print("Keine Änderungen – kein Push nötig.")

    except Exception as e:
        import traceback
        print(f"Fehler: {e}")
        traceback.print_exc()
    finally:
        browser.quit()


if __name__ == '__main__':
    main()
