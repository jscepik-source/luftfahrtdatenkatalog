# ✈️ Aviation Katalog — GitHub Pages

Automatisch aktualisierte Flughafen- und Kartenkataloge, gehostet via GitHub Pages.

**Basis-URL:** `https://jscepik-source.github.io/luftfahrtdatenkatalog/`

---

## 🌐 Seiten

| Seite | URL | Beschreibung | Datenquelle |
|---|---|---|---|
| [DFS VFR Katalog](index.html) | [/](https://jscepik-source.github.io/luftfahrtdatenkatalog/) | Alle deutschen VFR-Flugplätze mit Karten aus dem DFS BasicVFR AIP | DFS AIP BasicVFR |
| [NOTAM](notam.html) | [/notam.html](https://jscepik-source.github.io/luftfahrtdatenkatalog/notam.html) | Aktuelles DFS VFR-NOTAM-Heftchen als eingebettetes PDF | DFS VFR-Info |
| [Weltweiter Flughafen-Katalog](ourairports.html) | [/ourairports.html](https://jscepik-source.github.io/luftfahrtdatenkatalog/ourairports.html) | ~72.000 Flughäfen weltweit mit Runways, Frequenzen, Nav-Aids, METAR/TAF, NOTAMs | OurAirports + Aviation Weather Center |
| [EUROCONTROL Karten](eurocontrol.html) | [/eurocontrol.html](https://jscepik-source.github.io/luftfahrtdatenkatalog/eurocontrol.html) | Europäische ATC-Karten (ERC, URC, MUAC…) von EUROCONTROL Cartography | EUROCONTROL |
| [Austrocontrol Katalog](austrocontrol.html) | [/austrocontrol.html](https://jscepik-source.github.io/luftfahrtdatenkatalog/austrocontrol.html) | Österreichische Flugplatzkarten aus dem eAIP Austrocontrol | Austrocontrol eAIP |

---

## 🤖 Bots (automatische Aktualisierung)

| Bot | Aktualisiert | Intervall |
|---|---|---|
| `dfs_bot.py` | `dfs_katalog_export.json` → index.html | Alle 6h via GitHub Actions |
| `notam_bot.py` | `notam_info.json` → notam.html | Alle 6h via GitHub Actions |
| `nfl_bot.py` | `nfl_katalog.json` | Alle 6h via GitHub Actions |
| `eurocontrol_bot.py` | `eurocontrol_katalog_export.json` → eurocontrol.html | Lokal ausführen, dann pushen |
| `ourairports_bot.py` | `ourairports_export.json` → ourairports.html | Lokal ausführen, dann pushen |

---

## 📁 Dateistruktur

```
📦 luftfahrtdatenkatalog/
├── 🌐 index.html                     ← DFS VFR Flughafen-Katalog
├── 🌐 notam.html                     ← NOTAM PDF Viewer
├── 🌐 ourairports.html               ← Weltweiter Flughafen-Katalog
├── 🌐 eurocontrol.html               ← EUROCONTROL Karten-Katalog
├── 🌐 austrocontrol.html             ← Austrocontrol Katalog
│
├── 📊 dfs_katalog_export.json        ← Daten für index.html
├── 📊 notam_info.json                ← Daten für notam.html
├── 📊 nfl_katalog.json               ← NfL-Daten
├── 📊 eurocontrol_katalog_export.json← Daten für eurocontrol.html
├── 📊 ourairports_export.json        ← Daten für ourairports.html
├── 📊 austrocontrol_katalog_export.json← Daten für austrocontrol.html
│
├── 🤖 dfs_bot.py                     ← Scrapt DFS BasicVFR
├── 🤖 notam_bot.py                   ← Sucht aktuelles NOTAM PDF
├── 🤖 nfl_bot.py                     ← Scrapt NfL-Liste
├── 🤖 eurocontrol_bot.py             ← Scrapt EUROCONTROL Karten
├── 🤖 ourairports_bot.py             ← Lädt OurAirports CSV-Daten
│
└── ⚙️ .github/workflows/
    └── update-katalog.yml            ← GitHub Actions (alle 6h)
```

---

## ⚙️ GitHub Actions

Der Workflow `.github/workflows/update-katalog.yml` läuft automatisch **alle 6 Stunden** und aktualisiert DFS-Katalog, NOTAM und NfL. EUROCONTROL und OurAirports werden lokal ausgeführt und manuell gepusht.
