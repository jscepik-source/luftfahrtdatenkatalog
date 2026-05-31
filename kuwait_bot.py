"""
kuwait_bot.py – Kuwait AIP (DGCA – Directorate General of Civil Aviation)
Liest Karten für OKKK aus der statischen AIP-Seite.
Ausgabe: ok_katalog_export.json
"""

import json, os, re, subprocess, requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

AIP_PAGE = "https://dgca.gov.kw/AIP"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT   = "ok_katalog_export.json"
HEADERS  = {"User-Agent": "Mozilla/5.0", "Referer": AIP_PAGE}

OKKK_RE = re.compile(r'OKKK', re.I)


def extract_chart_name(context_text):
    """Extrahiert den Kartennamen aus dem Kontext 'AD 2.OKKK-N: CHART NAME'."""
    # Strip the "AD 2.OKKK-N: " prefix
    cleaned = re.sub(r'^AD\s*2?\.?\s*OKKK-[\d._]+[:\s]+', '', context_text, flags=re.I).strip()
    # Fallback: use the full context if nothing was stripped
    return cleaned or context_text.strip()


def main():
    print("Lade Kuwait AIP ...")
    r = requests.get(AIP_PAGE, timeout=20, headers=HEADERS)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    karten = {}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "blob" not in href or not OKKK_RE.search(href):
            continue

        # Find nearby heading text for chart name
        chart_name = ""
        el = a
        for _ in range(6):
            el = el.parent
            if el is None:
                break
            for tag in el.find_all(["h1","h2","h3","h4","h5","p","li","th","td","span"]):
                t = tag.get_text(strip=True)
                if t and len(t) > 5 and "Download" not in t and "PDF" not in t:
                    chart_name = extract_chart_name(t)
                    break
            if chart_name:
                break

        # Fallback to decoded filename
        if not chart_name:
            fname = unquote(href.split("/")[-1]).replace(".pdf", "")
            chart_name = extract_chart_name(fname)

        if chart_name and href not in karten.values():
            print(f"  {chart_name[:70]}")
            karten[chart_name] = href

    print(f"\n{len(karten)} Karten für OKKK gefunden.")

    if not karten:
        print("FEHLER: Keine Karten gefunden!")
        return

    katalog = {
        "OKKK": {
            "_url": AIP_PAGE,
            "karten": karten,
        }
    }

    pfad = os.path.join(REPO_DIR, OUTPUT)
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(katalog, f, indent=2, ensure_ascii=False)
    print(f"JSON gespeichert: {pfad}")

    _win_git = r"C:\Program Files\Git\cmd\git.exe"
    git = _win_git if os.path.isfile(_win_git) else "git"
    subprocess.run([git, "-C", REPO_DIR, "add", OUTPUT], check=True)
    r2 = subprocess.run([git, "-C", REPO_DIR, "commit",
                         "-m", "Kuwait AIP aktualisiert"])
    if r2.returncode == 0:
        subprocess.run([git, "-C", REPO_DIR, "push"], check=True)
        print("GitHub aktualisiert.")
    else:
        print("Keine Änderungen.")


if __name__ == "__main__":
    main()
