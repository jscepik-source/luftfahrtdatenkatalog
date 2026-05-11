"""
canada_bot.py – Kanada AIP (Nav Canada, navcanada.ca)
Liest aktuellen Part-3-Download-Link aus der CrownPeak-API.
Ausgabe: c_katalog_export.json
"""

import re, json, os, subprocess, requests, urllib.parse
from datetime import datetime, timezone

AIP_PAGE = "https://www.navcanada.ca/en/aeronautical-information/aip-canada.aspx"
PROXY    = "https://www.navcanada.ca/crownpeaksearchproxy.aspx"
CP_BASE  = "https://searchg2-restricted.crownpeak.net/navcanada-corporate-live/select"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "c_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0",
            "Referer": AIP_PAGE}

# Wichtigste kanadische Flughäfen (verweisen alle auf dieselbe Part-3-PDF)
AIRPORTS = [
    "CYYZ",  # Toronto Pearson
    "CYVR",  # Vancouver
    "CYUL",  # Montréal-Trudeau
    "CYYC",  # Calgary
    "CYEG",  # Edmonton
    "CYOW",  # Ottawa
    "CYWG",  # Winnipeg
    "CYQB",  # Québec City
    "CYHZ",  # Halifax
    "CYXE",  # Saskatoon
    "CYQR",  # Regina
    "CYJT",  # Stephenville
    "CYYT",  # St. John's
    "CYFC",  # Fredericton
    "CYZF",  # Yellowknife
]


def query_api(ftype, lang="en"):
    """Gibt alle Dokumente für einen AIP-Typ zurück (effdate, expdate, url)."""
    fq = [f"custom_s_aim_filetype:{ftype}", f"custom_s_language:{lang}"]
    fq_str = "&".join(f"fq={urllib.parse.quote(f)}" for f in fq)
    cp_url = f"{CP_BASE}?q=*&{fq_str}&wt=json&rows=20"
    r = requests.get(f"{PROXY}?q={urllib.parse.quote(cp_url)}",
                     timeout=20, headers=HEADERS)
    return r.json().get("response", {}).get("docs", []) if r.ok else []


def find_current(docs):
    """Gibt das zum jetzigen Zeitpunkt gültige Dokument zurück."""
    now = datetime.now(timezone.utc)
    best = None
    for doc in docs:
        eff = doc.get("custom_dt_aim_effdate")
        exp = doc.get("custom_dt_aim_expdate")
        if not eff:
            continue
        eff_dt = datetime.fromisoformat(eff.replace("Z", "+00:00"))
        exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00")) if exp else None
        if eff_dt <= now and (exp_dt is None or exp_dt > now):
            if best is None or eff_dt > datetime.fromisoformat(
                    best["custom_dt_aim_effdate"].replace("Z", "+00:00")):
                best = doc
    return best


def main():
    print("Suche aktuelles AIP Canada (Nav Canada) ...")
    karten = {}
    labels = {
        "AIPPart1": "AIP Canada – Part 1 General",
        "AIPPart2": "AIP Canada – Part 2 Enroute",
        "AIPPart3": "AIP Canada – Part 3 Aerodromes",
    }
    eff_label = None
    for ftype, label in labels.items():
        docs = query_api(ftype)
        doc = find_current(docs)
        if doc:
            url = doc["custom_s_url"]
            eff = doc["custom_dt_aim_effdate"][:10]
            exp = doc.get("custom_dt_aim_expdate", "")[:10]
            print(f"  {label}: {eff} – {exp}")
            print(f"    -> {url}")
            karten[label] = url
            if ftype == "AIPPart3":
                eff_label = eff
        else:
            print(f"  {label}: nicht gefunden")

    if not karten:
        print("FEHLER: Keine AIP-Dokumente gefunden!")
        return

    katalog = {
        icao: {"_url": AIP_PAGE, "karten": karten}
        for icao in AIRPORTS
    }
    print(f"\n  {len(AIRPORTS)} Flughäfen")

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    label = f"eff. {eff_label}" if eff_label else "aktuell"
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", f"Kanada AIP ({label}) aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
