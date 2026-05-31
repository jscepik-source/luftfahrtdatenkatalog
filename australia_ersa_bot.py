"""
australia_ersa_bot.py – Australien ERSA (Airservices Australia)
Erkennt die aktuelle AIRAC-Periode automatisch, kein Selenium nötig.
Ausgabe: y_katalog_export.json
"""

import re, json, os, subprocess, requests
from datetime import datetime
from bs4 import BeautifulSoup

AIP_ROOT = "https://www.airservicesaustralia.com"
INDEX_URL = AIP_ROOT + "/aip/aip.asp?pg=10"
REPO_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = "y_katalog_export.json"
HEADERS   = {"User-Agent": "Mozilla/5.0"}

MONTHS = {"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,
          "JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}


def parse_aip_date(s):
    """'19MAR2026' → datetime"""
    m = re.match(r"(\d{2})([A-Z]{3})(\d{4})", s)
    if not m:
        return None
    day, mon, yr = int(m.group(1)), MONTHS.get(m.group(2), 0), int(m.group(3))
    return datetime(yr, mon, day) if mon else None


def find_current_ersa_url():
    """Liest die Index-Seite und gibt die aktuelle ERSA-URL zurück."""
    r = requests.get(INDEX_URL, timeout=20, headers=HEADERS)
    # Alle pg=40 Links mit vdate
    matches = re.findall(r'href="(aip\.asp\?pg=40&(?:amp;)?vdate=(\d{2}[A-Z]{3}\d{4})&[^"]*)"', r.text)
    today = datetime.today()
    best_url, best_date = None, None
    for href, vdate in matches:
        d = parse_aip_date(vdate)
        if d and d <= today:
            if best_date is None or d > best_date:
                best_date = d
                best_url  = href.replace("&amp;", "&")
    return (AIP_ROOT + "/aip/" + best_url) if best_url else None, best_date


def main():
    print("Suche aktuelle ERSA-Periode ...")
    ersa_url, ersa_date = find_current_ersa_url()
    if not ersa_url:
        print("FEHLER: Keine aktuelle ERSA-Seite gefunden!")
        return
    print(f"  ERSA-Seite: {ersa_url}")
    print(f"  Datum:      {ersa_date.strftime('%d %b %Y')}")

    # ── Alle Chart-Links von der ERSA-Seite ─────────────────────────────────
    r = requests.get(ersa_url, timeout=30, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # href="/aip/current/ersa/FAC_YSSY_19MAR2026.pdf"
    pdf_re = re.compile(r"/aip/current/ersa/([A-Z]+)_([A-Z]{4})_(\d{2}[A-Z]{3}\d{4})\.pdf")

    katalog = {}
    for a in soup.find_all("a", href=True):
        m = pdf_re.search(a["href"])
        if not m:
            continue
        chart_type = m.group(1)   # FAC, RDS, …
        icao       = m.group(2)   # YSSY, YPAD, …
        date_str   = m.group(3)   # 19MAR2026
        pdf_url    = AIP_ROOT + a["href"]
        link_text  = a.get_text(strip=True) or f"{chart_type} {icao}"

        katalog.setdefault(icao, {"_url": pdf_url, "karten": {}})
        # FAC-Link als primäre _url setzen
        if chart_type == "FAC":
            katalog[icao]["_url"] = pdf_url
        katalog[icao]["karten"][link_text or f"{chart_type} {icao}"] = pdf_url

    print(f"  {len(katalog)} Flughäfen gefunden")

    if not katalog:
        print("WARNUNG: Keine Daten!")
        return

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    label = ersa_date.strftime("%d%b%Y").upper()
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", f"Australien ERSA ({label}) aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
