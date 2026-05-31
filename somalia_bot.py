"""
somalia_bot.py – Somalia AIP (SCAA, aip.scaa.gov.so)
Statisches eAIP, kein Selenium nötig.
Ausgabe: hc_katalog_export.json
"""

import re, json, os, subprocess, warnings, requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

MENU_URL = "https://aip.scaa.gov.so/eAIP/HC-menu-en-GB.html"
BASE_AP  = "https://aip.scaa.gov.so/eAIP/HC-AD-2.{icao}-en-GB.html"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "hc_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0"}
PDF_RE   = re.compile(r".*\.pdf", re.I)


def clean_name(s):
    """'Figure 9.\xa0 Aerodrome Chart – ICAO' → 'Aerodrome Chart – ICAO'"""
    s = s.replace("\xa0", " ").replace("\xc2", "").strip()
    s = re.sub(r"^[Ff]igure[\s\d.]+", "", s).strip()
    return s or s


def scrape_airport(icao):
    page_url = BASE_AP.format(icao=icao)
    try:
        r = requests.get(page_url, timeout=20, headers=HEADERS, verify=False)
        if r.status_code != 200:
            return {}
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        karten = {}
        for a in soup.find_all("a", href=PDF_RE):
            href = a["href"]
            if "graphics" not in href:
                continue
            pdf_url = urljoin(page_url, href)
            fig_div = a.find_parent("div", class_="Figure")
            if fig_div:
                title = fig_div.find("span", class_="Figure-title")
                chart_name = clean_name(title.get_text(strip=True)) if title else ""
            else:
                chart_name = ""
            if not chart_name:
                chart_name = href.split("/")[-1]
            karten[chart_name] = pdf_url
        return karten
    except Exception as e:
        print(f"    {icao}: Fehler – {e}")
        return {}


def main():
    print("Lade Somalia-AIP-Menü ...")
    r = requests.get(MENU_URL, timeout=15, headers=HEADERS, verify=False)
    r.encoding = "utf-8"
    icao_codes = sorted(set(re.findall(r"HC-AD-2\.([A-Z]{4})", r.text)))
    title = re.search(r"<title>([^<]+)", r.text)
    print(f"  {title.group(1).strip() if title else 'Somalia AIP'}")
    print(f"  {len(icao_codes)} Flughäfen: {icao_codes}")

    katalog = {}
    for i, icao in enumerate(icao_codes, 1):
        karten = scrape_airport(icao)
        ap_url = BASE_AP.format(icao=icao)
        print(f"  [{i:2d}/{len(icao_codes)}] {icao}: {len(karten)} Karten", flush=True)
        if karten:
            katalog[icao] = {"_url": ap_url, "karten": karten}

    print(f"\n  Gesamt: {len(katalog)} Flughäfen mit Karten")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", "Somalia AIP (SCAA) aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
