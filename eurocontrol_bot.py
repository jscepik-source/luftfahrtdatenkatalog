from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import subprocess

BASIS_URL = "https://www.eurocontrol.int"
KARTEN_URL = BASIS_URL + "/service/cartography"


def warte(browser):
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'a'))
    )
    time.sleep(0.5)


def alle_links(browser):
    return [(l.text.strip(), l.get_attribute('href'))
            for l in browser.find_elements(By.TAG_NAME, 'a')]


def durchlauf():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=options)
    katalog = {}

    try:
        browser.get(KARTEN_URL)
        warte(browser)

        # Alle Publikations-Links sammeln
        publikationen = {}
        for text, href in alle_links(browser):
            if href and '/publication/' in href and text and len(text) > 5:
                publikationen[text] = href

        print(f"{len(publikationen)} Publikationen gefunden")

        for name, pub_url in publikationen.items():
            print(f"  {name[:60]} ...", end=" ", flush=True)

            karten = {}
            try:
                browser.get(pub_url)
                warte(browser)

                for text, href in alle_links(browser):
                    if not href:
                        continue
                    # Direkte PDF-Links sammeln (keine archive_download – die brauchen Auth)
                    if href.lower().endswith('.pdf'):
                        label = text if text else href.split('/')[-1]
                        if not href.startswith('http'):
                            href = BASIS_URL + href
                        karten[label] = href
            except Exception:
                pass

            # Fallback: Publikationsseite selbst
            if not karten:
                karten["Auf EUROCONTROL öffnen"] = pub_url

            print(f"({len(karten)} Downloads)")
            katalog[name] = {
                "_url": pub_url,
                "karten": karten
            }

        with open("eurocontrol_katalog_export.json", "w", encoding="utf-8") as f:
            json.dump(katalog, f, indent=4, ensure_ascii=False)

        print(f"\nFertig! {len(katalog)} Publikationen gespeichert.")

        _win_git = r"C:\Program Files\Git\cmd\git.exe"
        git = _win_git if os.path.isfile(_win_git) else "git"
        subprocess.run([git, "add", "eurocontrol_katalog_export.json"], check=True)
        result = subprocess.run([git, "commit", "-m", "Automatische Aktualisierung Eurocontrol"])
        if result.returncode == 0:
            subprocess.run([git, "push"], check=True)
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
