# Quellenkatalog — vollständige Übersicht
### Alle im Projekt verwendeten Datenquellen, direkt aus dem Code extrahiert
**Projekt:** Luftfahrtdatenkatalog · Hochschule RheinMain · Modul Avionik
**Erzeugt:** automatisch aus dem Quellcode (kein manuelles Abtippen → keine Übertragungsfehler)
**Vollständige Liste:** siehe **`QUELLENKATALOG.csv`** (539 Einträge, in Excel/LibreOffice öffenbar)

---

## 1 · Zwei Ebenen von Quellen

Das Projekt nutzt bewusst **zwei getrennte Quellen-Ebenen** (siehe auch `ANLEITUNG_Website_mit_KI_bauen.md`, Teil O):

- **Ebene A — Technische Live-APIs:** was der Browser **zur Laufzeit automatisch** abruft (ADS-B, Wikipedia/Wikidata, Overpass, OpenAIP …). → 21 APIs, dokumentiert als „Steckbriefe" in der Anleitung.
- **Ebene B — Kuratierter Quellenkatalog:** die **redaktionell recherchierten offiziellen Informationsquellen** (nationale AIP, NOTAM, VFR, Statistik-Quellen …), nach Kriterien bewertet. → **Dieses Dokument + `QUELLENKATALOG.csv`.**

---

## 2 · Umfang auf einen Blick (aus dem Code gezählt)

| Kategorie | Einträge | Eindeutige Anbieter | Wo im Code |
|---|---|---|---|
| **AIP** (nationale Luftfahrthandbücher je Land) | **212** ICAO-Präfixe | **191** | `AIP_PREFIXES`, `AIP_SINGLE_LETTER` (ourairports.html) |
| **NOTAM-Portale** (national, je Land) | **113** ICAO-Präfixe | **93** | `NOTAM_PORTALE`, `NOTAM_PORTALE_SINGLE` (ourairports.html) |
| **VFR-Quellen** (Sichtflug-Karten/Portale) | **43** | — | `VFR_QUELLEN` (ourairports.html) |
| **Drohnen / UAV-Datenquellen** | **18** | — | `QUELLEN` (drohnen.html) |
| **Katalog-Quellen** (Statistik, Technik, Zertifizierung …) | **153** | — | `src(...)`-Objekte (Luftfahrt-Katalog) |
| **Summe** | **539** | | |

> Hinweis: „Präfixe" = ICAO-Code-Anfangsbuchstaben (z. B. `ED` = Deutschland, `LF` = Frankreich). Mehrere Präfixe können auf denselben Anbieter zeigen (z. B. mehrere `Z…`-Präfixe → CAAC China) — daher die niedrigere Zahl eindeutiger Anbieter.

### 2b · Vollständige Kategorie-Taxonomie des Recherche-Katalogs (Ebene B)

Die Recherche-Tabelle gliedert die Quellen in **elf Fachkategorien**. Anzahl laut Tabellen-Beschriftung (Zähler mit „ca." = in den Vorlagen nicht eindeutig lesbar):

| # | Kategorie | Quellen | Beispiel-Anbieter | Bezug auf der Website |
|---|---|---|---|---|
| 1 | **AIP** (national) | 191 Anbieter (Code) | DFS BasicAIP, ASECNA (17 Staaten), FAA d-TPP, SkyVector, Eurocontrol EAD | Flughäfen-Seite: AIP-Link je Land |
| 2 | **NOTAM** | **11** | AVWX, CheckWX, ICAO iSTARS, FAA DINS, autorouter, NOAA | NOTAM-Ansicht + nationale Portale |
| 3 | **Flugplan** | ca. 11 | Aviation Edge, Cirium, Eurocontrol NM B2B/PPS, FAA SWIM, IATA, ICAO Doc 4444/FIXM, Lufthansa API, OpenNav, STATFOR | Recherche-Ebene (Live-Flüge via ADS-B) |
| 4 | **Verkehr** | **8** | ADS-B Exchange, OpenSky, FlightAware, Plane Finder, Spire Aviation, DFS Stanly | Live-ADS-B (umgesetzt via airplanes.live) |
| 5 | **Luftraum** | **9** | OpenAIP, Eurocontrol AIRAC, Open Flightmaps, LXNAV, ChartFox, DHV | Lufträume-Seite |
| 6 | **Flugzeuge** | ca. 11 | ICAO Doc 8643, FAA Aircraft Registry, EASA Register, Planespotters, SKYbrary, TCDS | Flugzeug-Katalog |
| 7 | **Triebwerke** | **11** | CFM, GE Aviation, Pratt & Whitney, Rolls-Royce, Safran, Honeywell, ICAO EEDB, EASA/FAA TCDS | Triebwerks-Ansicht |
| 8 | **Technische Infos** | **18** | CS-25 / CS-E, FAR 25/33, RTCA DO-178C / DO-160, Jane's, NASA, EASA/FAA Certification Specs | Katalog „Technische Infos" |
| 9 | **Wetter** | **24** | AWC/NOAA (METAR/TAF/SIGMET), ECMWF, Meteoblue, Meteomatics, DWD, GAFOR, SkySight | METAR/TAF (umgesetzt via aviationweather.gov) |
| 10 | **Statistik** | **15** | Eurostat, DESTATIS, ICAO WATS, IATA Economics, Boeing/Airbus Forecast, NTSB, ASN | Statistik-Dashboard |
| 11 | **UAVs / Drohnen** | **17** (Code: 18) | OpenAIP UAV, DJI FlySafe, Dronetag, EASA/LBA/DFS/Dipul, Drone-Check | Drohnen-Seite |

**Zwei Umsetzungswege je Kategorie:**
- **Als kuratierte, bewertete Quellen-Seite** (aus `src(...)`-Daten): AIP, Flugzeuge, Triebwerke, Technische Infos, Statistik, Drohnen, Lufträume.
- **Als technisch umgesetztes Live-Feature** (Ebene-A-API): Verkehr → Live-ADS-B (airplanes.live), Wetter → METAR/TAF (aviationweather.gov), Flugplan → Registrierungs-Tracker (Flightradar24/adsbdb). Hier diente die Recherche als **Auswahl-/Bewertungsgrundlage**, umgesetzt wurde die jeweils beste browser-taugliche Quelle.

> Damit ist belegt: Es wurden **~11 Fachkategorien** systematisch recherchiert und je nach Eignung entweder als **bewertete Quellenliste** oder als **funktionierendes Feature** in die Website überführt.

---

## 3 · Abgleich mit der Recherche-Tabelle (Screenshot)

Die von dir gepflegte **Recherche-Tabelle** (Screenshot) und der **Code** passen zusammen:

- Die **AIP-Kategorie** der Tabelle entspricht `AIP_PREFIXES` (191 Anbieter, von `AACM Macau` über `ASECNA` (17 Staaten) bis `DFS BasicAIP`, `Eurocontrol EAD`, `FAA d-TPP/NASR`, `SkyVector`, `EUROCONTROL Cartography`).
- Die **NOTAM-Kategorie** existiert im Projekt **doppelt** und ist zu unterscheiden:
  - **NOTAM-Portale (national):** 113 länderspezifische Portale (`NOTAM_PORTALE`) — die offiziellen NOTAM-Quellen je Staat.
  - **NOTAM-Datendienste (technisch):** die „**11 Quellen**" aus dem Screenshot (AVWX, CheckWX, DFS AIM/NfL, Eurocontrol EAD, FAA DINS, ICAO NOTAMs, ICAO iSTARS, NOAA, autorouter.aero, notammap, SkyLink/RapidAPI) — das sind **maschinenlesbare NOTAM-APIs/Feeds** (Ebene A/B-Mischung), die bewertet wurden.

### Die Bewertungskriterien der Recherche-Tabelle
Deine Tabelle bewertet jede Quelle nach einheitlichen Kriterien (die Spalten):
**Inhalt · Zielgruppe · Format** (PDF / HTML-eAIP / XML-AIXM / REST-JSON / GeoJSON) **· Unique-ID-Schema** (ICAO-Code-Präfix, NOTAM-Nummer, FIR-ID) **· Verfügbarkeit/Login · AIRAC-Zyklus** (28 Tage) **· Abdeckung · Kosten · Bewertung (Sterne) · Link**.

Diese **Zusatzspalten** (Zielgruppe, Format, AIRAC, Bewertung, Bemerkung) liegen in deiner **Recherche-Tabelle**, **nicht** im Website-Code — der Code speichert je Quelle nur **Name + URL (+ Präfix)**. `QUELLENKATALOG.csv` enthält daher Name/Präfix/URL vollständig; die Bewertungsspalten können ergänzt werden (siehe §5).

---

## 4 · So liegt der Katalog im Code (Ebene B → Website)

Die Quellen sind als **Datenobjekte** hinterlegt und werden zur Laufzeit gerendert:

```javascript
// ourairports.html — je Land ein Eintrag
const AIP_PREFIXES = {
  'ED': { name: 'DFS AIP Deutschland', url: 'https://aip.dfs.de/basicAIP/' },
  'LF': { name: 'SIA AIP France',      url: 'https://www.sia.aviation-civile.gouv.fr/' },
  // … 212 Einträge
};

// Luftfahrt-Katalog — bewertete Quellen (Statistik etc.)
src(4,4,3,5,5, 'Eurostat – Air Transport Statistics', 'EU-Passagier-/Fracht-Statistiken …',
    'Behörden, Forscher', ['CSV','Excel','API'], 'Exzellente Open-Data-Quelle …',
    'https://ec.europa.eu/eurostat/…');   // Zahlen = Bewertung nach 5 Kriterien
```

Die Seite baut daraus automatisch die **aufklappbaren, bewerteten Quellen-Karten** mit **Filter-Chips, Suche und Sterne-Rating**.

---

## 5 · Optional: Recherche-Bewertungen mit dem Code zusammenführen

Wenn du deine **Recherche-Tabelle als CSV exportierst** (aus Excel/Google Sheets: „Als CSV speichern"), lässt sie sich mit `QUELLENKATALOG.csv` über den **Namen bzw. das ICAO-Präfix** zusammenführen — dann hast du **eine** Datei mit *sowohl* den technischen URLs aus dem Code *als auch* deinen Bewertungsspalten (Zielgruppe, Format, AIRAC, Sterne …). Sag Bescheid, dann übernehme ich den Abgleich.

---

## 6 · Dateien
- **`QUELLENKATALOG.csv`** — vollständige Liste aller 539 Quellen (Kategorie, Name, Präfix, Format, URL).
- **`ANLEITUNG_Website_mit_KI_bauen.md`** — Teil O: Quellen-Steckbriefe (technische APIs) + Katalog-Methodik.
- **`VERBESSERUNGEN_Praesentation.md`** — technische Ergebnis-Übersicht.

*Erzeugt durch automatische Extraktion aus `ourairports.html`, `drohnen.html`, `Luftfahrt_Katalog_FINAL_CLEAN_10.html`.*
