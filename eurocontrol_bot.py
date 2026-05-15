from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import subprocess

REPO_DIR   = os.path.dirname(os.path.abspath(__file__))
BASIS_URL  = "https://www.eurocontrol.int"
KARTEN_URL = BASIS_URL + "/service/cartography"


def warte(browser, timeout=10):
    WebDriverWait(browser, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, 'a'))
    )
    time.sleep(1)


def alle_links(browser):
    return [(l.text.strip(), l.get_attribute('href'))
            for l in browser.find_elements(By.TAG_NAME, 'a')]


def durchlauf():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    katalog = {}

    try:
        print("1. EUROCONTROL Cartography laden...")
        browser.get(KARTEN_URL)
        warte(browser)

        publikationen = {}
        for text, href in alle_links(browser):
            if href and '/publication/' in href and text and len(text) > 5:
                publikationen[text] = href

        print(f"{len(publikationen)} Publikationen gefunden")

        for name, pub_url in publikationen.items():
            print(f"  {name[:70]} ...", end=" ", flush=True)

            karten = {}
            try:
                browser.get(pub_url)
                warte(browser)

                for text, href in alle_links(browser):
                    if not href:
                        continue
                    if href.lower().endswith('.pdf'):
                        label = text if text else href.split('/')[-1]
                        if not href.startswith('http'):
                            href = BASIS_URL + href
                        karten[label] = href
            except Exception:
                pass

            if not karten:
                karten["Auf EUROCONTROL öffnen"] = pub_url

            print(f"({len(karten)} Downloads)")
            katalog[name] = {
                "_url": pub_url,
                "karten": karten
            }

        out_path = os.path.join(REPO_DIR, "eurocontrol_katalog_export.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(katalog, f, indent=2, ensure_ascii=False)

        print(f"\nFertig! {len(katalog)} Publikationen gespeichert.")

        _win_git = r"C:\Program Files\Git\cmd\git.exe"
        git = _win_git if os.path.isfile(_win_git) else "git"
        subprocess.run([git, "-C", REPO_DIR, "add", "eurocontrol_katalog_export.json"], check=True)
        result = subprocess.run([git, "-C", REPO_DIR, "commit", "-m", "EUROCONTROL-Karten aktualisiert"])
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


def main():
    import sys
    if '--loop' in sys.argv:
        while True:
            print("Starte Durchlauf...")
            durchlauf()
            print("Nächster Durchlauf in 6 Stunden.\n")
            time.sleep(6 * 60 * 60)
    else:
        durchlauf()


if __name__ == '__main__':
    main()
