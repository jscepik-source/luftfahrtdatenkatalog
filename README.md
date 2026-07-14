# ✈️ Luftfahrtdatenkatalog

Weltweiter, automatisch aktualisierter Katalog von Luftfahrtdatenquellen mit interaktiven Web-Ansichten (Flughäfen, Flugzeuge, Drohnen, Lufträume). Statische Single-Page-Web-App, gehostet über **GitHub Pages** — nur HTML/CSS/JavaScript, kein Backend.

**Live:** https://jscepik-source.github.io/luftfahrtdatenkatalog/
**Hochschule RheinMain · Modul Avionik**

> 📚 Ausführliche Bau-Doku: [`ANLEITUNG_Website_mit_KI_bauen.md`](ANLEITUNG_Website_mit_KI_bauen.md) · als Wiki unter [`wiki/`](wiki/)

---

## 🌐 Web-Seiten

| Seite | Datei | Inhalt |
|---|---|---|
| Start | `index.html` | Themen-Auswahl (4 Karten) |
| Flughäfen | `ourairports.html` | ~72.000 Flughäfen: Suche, Karte, METAR/TAF, NOTAM, Infrastruktur, Live-ADS-B, KI-Assistent |
| Flugzeuge | `Luftfahrt_Katalog_FINAL_CLEAN_10.html` | Muster-Katalog, ICAO Doc 8643, Triebwerke, Statistik, Live-Tracker |
| Drohnen | `drohnen.html` | UAV-/Drohnen-Datenquellen (kuratiert) |
| Lufträume | `luftraeume.html` | OpenAIP-Luftraumkarte (Vertikalprofil, Höhenfilter, Suche) |
| Zusatz | `notam.html`, `eurocontrol.html`, `austrocontrol.html`, `nfl.html` | NOTAM-/Länder-Ansichten |

---

## 🧭 Struktur des Repositorys

> **Hinweis:** Die Dateien liegen bewusst **flach im Wurzelverzeichnis**. GitHub Pages liefert von der Wurzel aus, und die Seiten laden ihre Bot-Daten über feste `raw.githubusercontent.com/.../main/<datei>.json`-URLs. Die folgende Gliederung ist die **logische Gruppierung** dieser Dateien.

### 🤖 Bots (Datenbeschaffung)
Python-Skripte, die Luftfahrtdaten scrapen/abrufen und als JSON ins Repo schreiben.

- **Generischer eAIP-Bot** — `eaip_bot.py`: ein Scraper für alle Länder mit EUROCONTROL-Standard-eAIP. Neue Länder = nur ein Config-Eintrag (kein neuer Bot nötig).
- **Länder-/Quellen-Spezialbots** (Nicht-Standard-AIPs) — `albania_bot.py`, `australia_ersa_bot.py`, `austrocontrol_bot.py`, `belgium_bot.py`, `benelux_bot.py`, `bhutan_bot.py`, `canada_bot.py`, `cayman_bot.py`, `china_flyisfp_bot.py`, `cuba_bot.py`, `cyprus_bot.py`, `japan_bot.py`, `kuwait_bot.py`, `libya_bot.py`, `nepal_bot.py`, `netherlands_bot.py`, `russia_bot.py`, `somalia_bot.py`, `southafrica_bot.py`, `thailand_bot.py`
- **Kern- & Betriebsbots** — `dfs_bot.py`, `notam_bot.py`, `nfl_bot.py`, `nfl_notams_bot.py`, `ourairports_bot.py`, `eurocontrol_bot.py`, `faa_bot.py`, `shv_bot.py`, `lxnav_bot.py`

### 📊 Daten-Exporte (Bot-Ausgaben)
JSON/GeoJSON, die von den Seiten zur Laufzeit geladen werden — z. B. `ourairports_export.json`, `nfl_notams_export.json`, `notam_info.json`, `eurocontrol_katalog_export.json`, `shv_airspace.geojson`, sowie die pro ICAO-Präfix erzeugten `*_katalog_export.json` (AIP-Kategorie).

### ⚙️ Konfiguration & Assets
`manifest.json`, `sw.js` (Service Worker / PWA), `icon.svg`, `og-image.png`, `sitemap.xml`, `robots.txt`, `.nojekyll`, `zeitstempel.js`, `planes/` (Flugzeug-Grafiken für die Flugzeug-Seite), `requirements.txt`.

### 🔁 Automatisierung
`.github/workflows/update-katalog.yml` — führt die Bots **alle 6 Stunden** aus und committet aktualisierte JSONs automatisch.

---

## 🔄 Datenfluss

```
Bot (Python)  ──▶  <name>_export.json  ──▶  Seite lädt per fetch()  ──▶  Anzeige
   ▲                                                 
   └── GitHub Actions (alle 6 h) oder lokal ausführen + pushen
```

---

## 🛠 Lokal entwickeln

```bash
# Bots benötigen Python-Abhängigkeiten
pip install -r requirements.txt

# Einen Bot ausführen (schreibt sein <name>_export.json)
python ourairports_bot.py
```

> **Wichtig:** Die Bots (GitHub Actions) pushen selbst auf `main`. Vor eigenem Push erst `git fetch` + `git merge origin/main`, sonst wird der Push abgelehnt. Die Bots ändern nur Daten-JSONs, nicht die HTML-Seiten → i. d. R. konfliktfrei.

---

## 🔐 Sicherheit

Schlüsselpflichtige Funktionen (OpenAIP-Lufträume, KI-Assistent) laufen **nicht** über geteilte Zugangsdaten: Nutzer hinterlegen einen eigenen, kostenlosen Key (nur im Browser-`localStorage`, nie im Code). Details: [`wiki/10-Sicherheit.md`](wiki/10-Sicherheit.md).
