"""
LXNAV Datenbank-Bot
Scrapet die neueste .asapt Airspace+Airport-Datenbank von LXNAV
und speichert URL + Datum in lxnav_latest.json
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone

BASE = "https://gliding.lxnav.com"
PAGE = f"{BASE}/lxdownloads/databases/"

def scrape():
    res = requests.get(PAGE, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    entries = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"\.asapt", href, re.IGNORECASE):
            continue
        url = href if href.startswith("http") else BASE + ("" if href.startswith("/") else "/") + href
        # Label aus Linktext oder umgebender Zeile
        label = a.get_text(strip=True)
        if not label:
            row = a.find_parent(["tr", "li", "div"])
            label = row.get_text(" ", strip=True)[:80] if row else url.split("/")[-1]
        entries.append({"label": label, "url": url})

    if not entries:
        print("Keine .asapt-Links gefunden — Seitenstruktur prüfen")
        return

    latest = entries[0]
    data = {
        "label":   latest["label"],
        "url":     latest["url"],
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "alle":    entries[:5]
    }
    with open("lxnav_latest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Gespeichert: {latest['label']} -- {latest['url']}")

if __name__ == "__main__":
    scrape()
