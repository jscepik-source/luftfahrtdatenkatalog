"""
china_flyisfp_bot.py – China eAIP (eaip.flyisfp.com)
Scrapt alle chinesischen Flughafen-Karten.
Ausgabe: zb_katalog_export.json
"""

import json, os, re, subprocess, time, requests
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
URL      = "https://eaip.flyisfp.com/#/eAIP"
OUTPUT   = "zb_katalog_export.json"
ICAO_RE  = re.compile(r'\b(Z[A-Z]{3})\b')


def make_browser():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    if _mgr:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return webdriver.Chrome(options=opts)


def perf_requests(browser):
    """Alle Netzwerk-Anfragen aus dem CDP-Performance-Log."""
    result = []
    try:
        for entry in browser.get_log("performance"):
            msg = json.loads(entry["message"])
            if msg["message"]["method"] == "Network.requestWillBeSent":
                req = msg["message"]["params"].get("request", {})
                u = req.get("url", "")
                m = req.get("method", "GET")
                if u:
                    result.append((m, u))
    except Exception:
        pass
    return result


def ist_api_url(url):
    return any(x in url for x in ['/api/', '.json', '/list', '/tree', '/airport', '/chart',
                                    '/file', '/pdf', '/eaip', '/download', '/task'])


def versuche_direkte_api(base):
    """Testet bekannte API-Endpunkt-Muster direkt per requests."""
    kandidaten = [
        f"{base}/api/airports",
        f"{base}/api/eaip/airports",
        f"{base}/api/aerodromes",
        f"{base}/api/tree",
        f"{base}/api/v1/airports",
        f"{base}/api/chart/list",
        f"{base}/eaip/api/airports",
    ]
    headers = {"Accept": "application/json", "Referer": URL}
    for url in kandidaten:
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("application/json"):
                print(f"  API gefunden: {url}")
                return url, r.json()
        except Exception:
            pass
    return None, None


def verarbeite_api_liste(data):
    """Versucht, Flughafen-Liste aus verschiedenen JSON-Strukturen zu extrahieren."""
    katalog = {}
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                icao = (item.get('icao') or item.get('ident') or item.get('code') or '').upper()
                if ICAO_RE.match(icao):
                    katalog[icao] = {
                        '_url': item.get('url') or item.get('link') or URL,
                        'karten': {}
                    }
    elif isinstance(data, dict):
        for key, val in data.items():
            if ICAO_RE.match(key.upper()):
                katalog[key.upper()] = {'_url': URL, 'karten': {}}
    return katalog


def main():
    browser = make_browser()
    katalog = {}

    try:
        print(f"Lade {URL} ...")
        browser.get(URL)
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(10)

        # ── 1. Netzwerk-Diagnose ─────────────────────────────────────────────
        alle_requests = perf_requests(browser)
        api_calls = [(m, u) for m, u in alle_requests if ist_api_url(u)]
        print(f"  Netzwerk-Anfragen: {len(alle_requests)} gesamt, {len(api_calls)} API-Calls")
        api_basis = "https://eaip.flyisfp.com"
        for method, u in api_calls:
            print(f"    [{method}] {u}")

        # ── 2. Direkte API-Suche ─────────────────────────────────────────────
        api_url, api_data = versuche_direkte_api(api_basis)
        if api_data:
            katalog = verarbeite_api_liste(api_data)
            print(f"  Via API: {len(katalog)} Flughäfen")

        # ── 3. DOM – alle <a>-Tags ───────────────────────────────────────────
        for a in browser.find_elements(By.TAG_NAME, 'a'):
            text = (a.text or '').strip()
            href = a.get_attribute('href') or ''
            m = ICAO_RE.search(text + ' ' + href)
            if not m:
                continue
            icao = m.group(1)
            if href and 'javascript' not in href and href not in ('#', ''):
                katalog.setdefault(icao, {'_url': URL, 'karten': {}})
                name = text or href.split('/')[-1]
                katalog[icao]['karten'][name] = href
        print(f"  Nach DOM-Links: {len(katalog)} Flughäfen")

        # ── 4. Expand-Button suchen und klicken ──────────────────────────────
        for btn_css in ['[class*="expand"]', '[class*="unfold"]', '[class*="all"]',
                         '[title*="Expand"]', '[title*="All"]']:
            try:
                btn = browser.find_element(By.CSS_SELECTOR, btn_css)
                btn.click()
                time.sleep(3)
                print(f"  Expand-Button geklickt: {btn_css}")
                break
            except Exception:
                pass

        # ── 5. Tree-Knoten traversieren ──────────────────────────────────────
        for css in ['.el-tree-node__label', '.ant-tree-title', '.rc-tree-title',
                    '[class*="tree-label"]', '[class*="node-label"]', '[class*="filename"]']:
            nodes = browser.find_elements(By.CSS_SELECTOR, css)
            if not nodes:
                continue
            hits = 0
            for node in nodes:
                text = (node.text or '').strip()
                m = ICAO_RE.search(text)
                if m:
                    icao = m.group(1)
                    katalog.setdefault(icao, {'_url': URL, 'karten': {}})
                    # Ist es ein Karten-Eintrag (Name enthält mehr als nur den ICAO-Code)?
                    if len(text) > 6:
                        katalog[icao]['karten'][text] = URL
                    hits += 1
            if hits:
                print(f"  Tree '{css}': {hits} ICAO-Treffer")
                break

        # ── 6. JavaScript: Vue-Tree-Daten direkt auslesen ───────────────────
        js_ergebnis = browser.execute_script(r"""
            try {
                // ElementUI Tree (Vue 2)
                var treeEl = document.querySelector('.el-tree');
                if (treeEl && treeEl.__vue__ && treeEl.__vue__.store) {
                    var labels = [];
                    function collect(node) {
                        if (node.data && node.data.label) labels.push(node.data.label);
                        else if (node.label) labels.push(node.label);
                        (node.childNodes || []).forEach(collect);
                    }
                    collect(treeEl.__vue__.store.root);
                    return JSON.stringify({fw: 'el-tree-vue2', labels: labels});
                }

                // Vue 3 (Naive UI / Element Plus)
                function getVue3Data(el) {
                    if (!el) return null;
                    var vnode = el._vei || el.__vueParentComponent;
                    if (vnode) return JSON.stringify({fw: 'vue3'});
                    return null;
                }
                var v3 = getVue3Data(document.querySelector('[class*="tree"]'));
                if (v3) return v3;

                // Globale Variablen scannen
                var globals = Object.keys(window).filter(k =>
                    k.toLowerCase().includes('store') ||
                    k.toLowerCase().includes('airport') ||
                    k.toLowerCase().includes('aip'));
                return JSON.stringify({fw: 'unknown', globals: globals.slice(0, 10),
                    bodySnippet: document.body.innerHTML.substring(0, 800)});
            } catch(e) {
                return JSON.stringify({error: String(e)});
            }
        """)

        if js_ergebnis:
            try:
                d = json.loads(js_ergebnis)
                fw = d.get('fw', '?')
                print(f"  Framework: {fw}")

                if 'labels' in d:
                    print(f"  Tree-Labels ({len(d['labels'])}): {d['labels'][:5]}")
                    for label in d['labels']:
                        m = ICAO_RE.search(str(label))
                        if m:
                            icao = m.group(1)
                            katalog.setdefault(icao, {'_url': URL, 'karten': {}})
                            if len(label) > 6:
                                katalog[icao]['karten'][label] = URL

                if 'globals' in d:
                    print(f"  Globale Vars: {d['globals']}")

                if 'bodySnippet' in d:
                    snippet = d['bodySnippet']
                    print(f"  Body-Ausschnitt:\n{snippet[:600]}")
                    # ICAO-Codes im HTML suchen
                    icao_im_html = sorted(set(ICAO_RE.findall(snippet)))
                    if icao_im_html:
                        print(f"  ICAO-Codes im HTML: {icao_im_html[:20]}")
                        for icao in icao_im_html:
                            katalog.setdefault(icao, {'_url': URL, 'karten': {}})

            except Exception as e:
                print(f"  JS-Parse-Fehler: {e} – Rohdaten: {js_ergebnis[:300]}")

        # ── 7. Download-Menü versuchen ───────────────────────────────────────
        try:
            dl_btn = browser.find_element(By.XPATH,
                '//*[contains(text(),"DOWNLOAD") or contains(text(),"Download") or contains(text(),"下载")]')
            dl_btn.click()
            time.sleep(3)
            # Neue Links nach Klick erfassen
            for a in browser.find_elements(By.TAG_NAME, 'a'):
                href = a.get_attribute('href') or ''
                text = (a.text or '').strip()
                m = ICAO_RE.search(text + ' ' + href)
                if m and href and '.pdf' in href.lower():
                    icao = m.group(1)
                    katalog.setdefault(icao, {'_url': URL, 'karten': {}})
                    katalog[icao]['karten'][text or href.split('/')[-1]] = href
            print("  DOWNLOAD-Menü geklickt und ausgewertet")
        except Exception:
            pass

        print(f"\n  Gesamt: {len(katalog)} Flughäfen gefunden")

    finally:
        browser.quit()

    if not katalog:
        print("WARNUNG: Keine Daten – Bot braucht Anpassung (Diagnose-Output oben prüfen)")
        return

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad} ({len(katalog)} Flughäfen)")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, '-C', REPO_DIR, 'add', OUTPUT], check=True)
    r = subprocess.run([git, '-C', REPO_DIR, 'commit', '-m', 'China eAIP (flyisfp) aktualisiert'])
    if r.returncode == 0:
        subprocess.run([git, '-C', REPO_DIR, 'push'], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine neuen Änderungen.")


if __name__ == '__main__':
    main()
