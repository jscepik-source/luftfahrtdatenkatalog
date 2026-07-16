# Von Null zur fertigen Website — vollständige Anleitung
### Wie der Luftfahrtdatenkatalog Schritt für Schritt mit KI gebaut wurde
**Projekt:** Luftfahrtdatenkatalog · Hochschule RheinMain · Modul Avionik
**Ergebnis:** Statische Single-Page-Webanwendung auf GitHub Pages — nur HTML/CSS/JavaScript, kein Backend.
**Live:** https://jscepik-source.github.io/luftfahrtdatenkatalog/
**Zielgruppe dieses Dokuments:** komplette Nachvollziehbarkeit — es wird **nichts** vorausgesetzt außer einem Computer mit Internet.

> ## 🚀 Ganz neu? **Zuerst den Schnellstart ausführen.**
> Wenn du **bei Null** anfängst (kein GitHub-Konto, kein Git, kein Editor), arbeite **erst** die kompakte Schritt-für-Schritt-Anleitung **[`SCHNELLSTART.md`](SCHNELLSTART.md)** durch. Sie bringt dich in ~45 Minuten von Null bis zur ersten **live sichtbaren Seite** — mit genauen Links und Screenshot-Stellen.
> **Danach hierher zurückkehren:** Diese Anleitung baut ab **[Teil E](#teil-e--arbeitsweise-mit-der-ki-der-wichtigste-teil)** die eigentliche Website Feature für Feature. *(Teil A–D unten sind die ausführliche Fassung dessen, was der Schnellstart kompakt zeigt — du kannst sie überspringen, wenn der Schnellstart klappte.)*

> **Lesehinweis:** Die Anleitung ist chronologisch. Wer bei Null startet, arbeitet Teil A→Q der Reihe nach ab. Jeder Bau-Schritt hat: **Ziel → Prompt (wörtlich verwendbar) → Datenquelle → Prüfen → typische Fehler.**
>
> **Auch als Wiki:** Dieselben Inhalte liegen als navigierbares **GitHub-Wiki** im Ordner [`wiki/`](wiki/) (Einzelseiten mit Sidebar und Querverweisen). Diese Datei ist die zusammenhängende Langfassung.

---

# INHALT

- **[🚀 SCHNELLSTART](SCHNELLSTART.md)** — bei Null anfangen: in 8 Schritten zur ersten Live-Seite · **zuerst ausführen**

- **Teil A** — Werkzeuge installieren (von absolut Null)
- **Teil B** — Git & GitHub verstehen (Minimalwissen)
- **Teil C** — Repository anlegen & GitHub Pages aktivieren
- **Teil D** — Die erste Seite live bringen (Erfolgserlebnis)
- **Teil E** — Arbeitsweise mit der KI (der wichtigste Teil)
- **Teil F** — Startseite bauen
- **Teil G** — Flughäfen-Seite bauen (in 8 Ausbaustufen)
- **Teil H** — Flugzeug-Katalog bauen (in 7 Ausbaustufen)
- **Teil I** — Drohnen-Seite bauen
- **Teil J** — Lufträume-Karte bauen
- **Teil K** — Übergreifend: Navigation, „Typ weltweit", Animationen
- **Teil L** — Externe Dienste einrichten (OpenAIP, Groq, Cloudflare Worker)
- **Teil M** — Automatisierung: Bots via GitHub Actions
- **Teil N** — Sicherheit
- **Teil O** — Kompletter Datei- & API-Überblick
- **Teil P** — Fehlerbehebung (Troubleshooting)
- **Teil Q** — Der gesamte Prompt-Ablauf als Checkliste

---

# TEIL A · Werkzeuge installieren (von absolut Null)

Du brauchst vier Dinge. Installationszeit gesamt ca. 30–45 Minuten.

### A.1 · Ein GitHub-Konto
1. Auf **github.com** gehen → **Sign up**.
2. Benutzername (z. B. `dein-name`), E-Mail, Passwort. Kostenlos.
3. E-Mail bestätigen.
→ GitHub speichert deinen Code und hostet die Website kostenlos (GitHub Pages).

### A.2 · Git (Versionskontrolle)
- **Windows:** git-scm.com → „Download for Windows" → Installer ausführen (alle Standard-Optionen bestätigen).
- **Mac:** Terminal öffnen, `git --version` eingeben → falls nicht vorhanden, installiert macOS es auf Nachfrage.
- Prüfen: Terminal/Eingabeaufforderung öffnen, `git --version` → es sollte eine Versionsnummer erscheinen.
- Einmalig einrichten:
  ```bash
  git config --global user.name "Dein Name"
  git config --global user.email "deine@email.de"
  ```

### A.3 · Ein Code-Editor
- **VS Code** empfohlen: code.visualstudio.com → herunterladen, installieren.

### A.4 · Ein KI-Coding-Assistent
Der Assistent schreibt und ändert die Dateien direkt im Projekt. Optionen:
- **Claude Code** (Kommandozeile oder VS-Code-Erweiterung) — in diesem Projekt verwendet.
- Alternativ **Cursor** (KI-Editor) oder die **Claude-/ChatGPT-Weboberfläche** (dann kopierst du Code selbst in die Dateien).

→ Für „genau diese Website" ist ein Assistent ideal, der **Dateien direkt bearbeiten** kann (Claude Code / Cursor), weil das Projekt aus wenigen, aber großen HTML-Dateien besteht.

---

# TEIL B · Git & GitHub — das Minimalwissen

Du brauchst nur fünf Begriffe:
- **Repository (Repo):** der Projektordner, den GitHub verwaltet.
- **Commit:** ein gespeicherter Stand mit Nachricht („was hab ich geändert").
- **Push:** deine Commits zu GitHub hochladen.
- **Pull / Fetch + Merge:** Änderungen von GitHub holen (wichtig, wenn Bots oder Teammitglieder committen).
- **Branch:** eine Arbeitslinie (wir arbeiten hier auf `main`).

Die einzigen vier Befehle im Alltag:
```bash
git add DATEINAME        # Änderung vormerken
git commit -m "Nachricht" # Stand speichern
git fetch && git merge origin/main   # fremde Änderungen holen (Bots!)
git push                 # hochladen
```
> **Merkregel für dieses Projekt:** Die automatischen Bots committen regelmäßig selbst. **Vor jedem Push** deshalb erst `git fetch` + `git merge origin/main`, sonst wird der Push abgelehnt.

---

# TEIL C · Repository anlegen & GitHub Pages aktivieren

1. Auf GitHub: **New repository** → Name z. B. `luftfahrtdatenkatalog` → **Public** → „Add a README" ankreuzen → **Create**.
2. Repo lokal holen (klonen):
   ```bash
   cd Desktop
   git clone https://github.com/DEIN-NAME/luftfahrtdatenkatalog.git "webseite avionik"
   cd "webseite avionik"
   ```
3. **GitHub Pages einschalten:** Repo → **Settings** → **Pages** → „Source: Deploy from a branch" → Branch **main**, Ordner **/(root)** → **Save**.
4. Nach ~1 Minute ist die Seite unter `https://DEIN-NAME.github.io/luftfahrtdatenkatalog/` erreichbar (noch leer).

---

# TEIL D · Die erste Seite live bringen (Erfolgserlebnis)

Bevor die KI loslegt, einmal den kompletten Kreislauf selbst durchspielen:

1. In VS Code im Projektordner eine Datei `index.html` anlegen mit:
   ```html
   <!doctype html><html lang="de"><meta charset="utf-8">
   <title>Test</title><h1>Hallo Luftfahrtdatenkatalog</h1>
   ```
2. Speichern, dann:
   ```bash
   git add index.html
   git commit -m "Erste Testseite"
   git push
   ```
3. `https://DEIN-NAME.github.io/luftfahrtdatenkatalog/` neu laden → „Hallo …" erscheint.

→ Ab jetzt gilt für **jede** Änderung derselbe Dreisatz: **speichern → commit → push**. (Der KI-Assistent macht das Bearbeiten und oft auch das Committen für dich.)

---

# TEIL E · Arbeitsweise mit der KI (der wichtigste Teil)

Der Rahmen wird **einmal** gesetzt, dann wird **iterativ** gebaut. Immer nur ein Feature, prüfen, weiter.

> **PROMPT E.0 — Projektrahmen (einmal zu Beginn, immer im Hinterkopf):**
> „Ich baue ein studentisches Uni-Projekt (Hochschule RheinMain, Modul Avionik): einen weltweiten **Luftfahrtdatenkatalog** als **statische Website** für **GitHub Pages** — nur HTML/CSS/JavaScript, **kein Backend, keine Datenbank, kein Build-Tool**. Jede Seite ist eine einzelne, in sich geschlossene `.html`-Datei mit eingebettetem CSS und JavaScript (Vanilla, keine Frameworks). Nutze ausschließlich **kostenlose, CORS-freie öffentliche APIs**, die direkt aus dem Browser funktionieren. Schreibe sauberen, kommentierten Code mit **Fallback/Fehlerbehandlung**. Sag mir bei jeder API vorab, ob sie ohne Key und mit CORS funktioniert. Design: modern, clean, responsive, Dark-Mode. Arbeite **schrittweise** — wir bauen Feature für Feature."

**Regeln, die den Unterschied machen (siehe auch Teil Q):**
- Nach jedem Prompt **im Browser prüfen**, erst dann weiter.
- Datenquellen **konkret** vorgeben (die KI rät sonst tote Endpunkte).
- Fehler **mit konkretem Beispiel** melden (welcher Flughafen, welches Flugzeug, welcher Klick).

---

# TEIL F · Startseite (`index.html`)

> **PROMPT F.1:** „Baue `index.html` als **Themen-Auswahlseite** mit vier großen anklickbaren Karten: **Flughäfen** (→ `ourairports.html`), **Flugzeuge** (→ Katalog), **Drohnen** (→ `drohnen.html`), **Lufträume** (→ `luftraeume.html`). Hero mit Farbverlauf, responsive CSS-Grid, Dark-Mode über `prefers-color-scheme`, Icons als Inline-SVG, Hover-Effekte, Footer mit Impressum."

> **PROMPT F.2:** „Füge eine sanfte, gestaffelte Einblende-Animation beim Laden hinzu (Hero + Karten faden nacheinander ein). `prefers-reduced-motion` respektieren."

**Prüfen:** vier Karten sichtbar, Links (kommen später) angelegt, Dark-Mode reagiert auf System-Einstellung.

---

# TEIL G · Flughäfen-Seite (`ourairports.html`) — in 8 Ausbaustufen

Das ist das Kernstück. **Jede Stufe einzeln bauen und prüfen.**

### G.1 · Daten & Suche
> „Baue `ourairports.html`: durchsuchbarer Katalog von **~72.000 Flughäfen weltweit** aus dem **OurAirports-CSV** (`https://davidmegginson.github.io/ourairports-data/airports.csv`). Sofort-Suche (ICAO, IATA, Name, Stadt, Land). Ergebnisliste mit **Infinite-Scroll** (~50 pro Batch). Filter-Chips nach Flughafentyp, Kontinent-Auswahl, Ergebniszähler."
- **Datenquelle:** OurAirports-CSV (frei, CORS ok). Beim ersten Laden parsen und im Speicher halten.
- **Prüfen:** „EDDF" eingeben → Frankfurt erscheint sofort.

### G.2 · Aufklappbare Detailkarte + Leaflet
> „Mach jeden Treffer aufklappbar: **Leaflet-Karte** (OpenStreetMap-Kacheln + optional Esri-Satellit), Pisten (Länge/Belag/ILS), Frequenzen, Elevation, Koordinaten, externe Links (SkyVector, Google Maps, ChartFox)."
- **Bibliothek:** Leaflet per CDN einbinden (`unpkg.com/leaflet@1.9.4`).
- **Prüfen:** Karte lädt beim Aufklappen; Marker sitzt korrekt.

### G.3 · Wetter (METAR/TAF)
> „Ergänze **Live-METAR und TAF** von `aviationweather.gov` mit dekodierter, lesbarer Darstellung (Wind, Sicht, Wolken, Temperatur, QNH)."

### G.4 · NOTAM / AIP-Links
> „Verlinke pro Land die passende **NOTAM/AIP-Quelle** (DFS für Deutschland, Eurocontrol, Austrocontrol …) und binde deutsche eAIP-Karten ein, wo verfügbar."

### G.5 · Infrastruktur aus OpenStreetMap (Overpass)
> „Lade pro Flughafen die **Infrastruktur aus OpenStreetMap** über die **Overpass-API**: Terminals, Gates, Tower, Betankung, Radar, Navaids (ILS/VOR/NDB/DME). Auf die Karte zeichnen und kategorisiert auflisten. Nutze mehrere Overpass-Spiegelserver als Fallback. **Wichtig:** Terminals sind in OSM teils `aeroway=terminal`, teils `building=terminal` — beide abfragen."
- **Prüfen:** EDDF → Terminals 1 **und** 2 erscheinen.

### G.6 · Live-ADS-B-Radar
> „Baue ein **Live-ADS-B-Radar**: aktuelle Flugzeuge im Umkreis von `https://api.airplanes.live/v2/point/<lat>/<lon>/<radius>` (CORS-frei, kein Key; `api.adsb.lol` als Fallback). Zeige sie als drehbare Flugzeug-Marker mit **flüssiger 60-fps-Animation per Dead-Reckoning** (zwischen Updates entlang Kurs+Geschwindigkeit weiterrechnen). Zusätzlich Live-Flugliste: Callsign, Kennzeichen, Typ, Höhe, Geschwindigkeit, Flugphase (farbcodiert). Auto-Refresh."
- **Prüfen:** Großflughafen mit Verkehr (EDDF/EDDM) → Flugzeuge bewegen sich.

### G.7 · Verlinkung ins Flugzeug (Deep-Links)
> „Mach in der Live-Flugliste **Kennzeichen und Flugzeugtyp anklickbar**: Klick auf den **Typ** öffnet im Katalog nur die passende Typ-Karte, Klick auf das **Kennzeichen** öffnet dort nur den Live-Tracker dieses Flugzeugs (per URL-Parameter `?q=` bzw. `?reg=`)."

### G.8 · KI-Assistent (optional)
> „Baue einen KI-Chat ('AeroGuide') zu Luftfahrtfragen. Der API-Schlüssel darf **nicht** im Client stehen — Anfrage über einen **Cloudflare Worker** (Schlüssel als Umgebungsvariable). Fallback-Anbieter einbauen." *(Einrichtung → Teil L.)*

---

# TEIL H · Flugzeug-Katalog — in 7 Ausbaustufen

### H.1 · Grundgerüst
> „Baue einen Flugzeug-Katalog (eigene `.html`): Datenobjekt im JS mit Flugzeugmustern (Name, Hersteller, Erstflug, technische Daten, Bewertung). Kategorien, Filter-Chips, Suche, aufklappbare Detailkarten mit dezenter Animation."

### H.2 · Fotos automatisch (mit Fallback + Logo-Filter)
> „Lade Fotos automatisch von **Wikipedia** (`api/rest_v1/page/summary/<Titel>` / `pageimages`). Baue einen **Fallback**: wenn eine Bild-URL scheitert (viele Wikimedia-`thumb`-URLs liefern HTTP 400), lade ein funktionierendes Thumbnail über die Wikipedia-REST-API nach. **Filtere Firmenlogos**; ist das Titelbild ein Logo, hole ein echtes Foto aus **Wikimedia Commons** (`generator=search`, Datei-Namespace)."

### H.3 · Daten aus Wikidata
> „Reichere jede Karte beim Aufklappen mit **Wikidata** an: Wikipedia-Titel → QID (`pageprops`) → Eigenschaften (`wbgetentities`): Länge (P2043), Spannweite (P2050), Höhe (P2048), Stückzahl (P1092). Nur zuverlässige Einheiten. Kuratierte Werte haben Vorrang. CORS via `origin=*`."

### H.4 · ICAO Doc 8643 & Triebwerke (mit Foto)
> „Baue eine **ICAO-Doc-8643-Ansicht** (alle Typencodes) und eine **Triebwerks-Ansicht**. Jedes Triebwerk mit **Foto** (Wikipedia-Suche → Foto; Logo-Filter; Commons-Fallback bei Logo, z. B. GE90)."

### H.5 · Statistik-Dashboard
> „Werte die Statistik-Seite auf: **Dashboard mit echten Diagrammen**, live aus den Katalog-Daten berechnet (Flugzeuge nach Jahrzehnt, Top-Hersteller, Triebwerke nach Typ) + Kennzahlen. **Pure CSS/SVG-Balken, keine Chart-Bibliothek**, animiert, `prefers-reduced-motion`."

### H.6 · Live-Tracker
> „Tracker: Nutzer gibt **Registrierung** ein → **letzte Flüge + Mode-S-Code + Flugzeugdaten**. Quellen (funktionieren aus dem Browser): Flightradar24 inoffiziell (`flight/list.json?query=<REG>&fetchBy=reg`) und `adsbdb.com`. Beide CORS `*`."

### H.7 · „Typ weltweit" integrieren
> „Integriere die 🌍-Funktion (siehe Teil K.2) auch hier: fester Button in der Leiste + 🌍-Chip an jedem ICAO-Typencode."

---

# TEIL I · Drohnen-Seite (`drohnen.html`)

> „Baue `drohnen.html`: Marktübersicht von **UAV-/Drohnen-Datenquellen** (Datenobjekt im JS), gruppiert nach Kategorie (Tracking/Remote-ID, Geo-Zonen, Regeln, Behörden, Wetter, NOTAMs). Filter-Chips mit **datengetriebenen Zählern**, Suche, **einklappbare Kategorie-Gruppen**, aufklappbare Detailkarten, Barrierefreiheit (Screenreader-Label, Tastatur-Fokus). Für Karten-Quellen eine kleine Leaflet-Karte mit OpenAIP-Lufträumen."

---

# TEIL J · Lufträume-Karte (`luftraeume.html`)

> „Baue `luftraeume.html`: **Vollbild-Leaflet-Weltkarte** der Lufträume (ICAO-Klassen A–G, CTR, TMA, Restricted/Prohibited/Danger) auf Basis von **OpenAIP** (Kachel-Layer + klickbare Polygone via `api.core.openaip.net`, **benötigt API-Key** → Teil L.1). Filter nach Land, Typ, Klasse. Farbcodierte, **einklappbare Legende**, Ortssuche via Nominatim. **Karte möglichst groß halten** (Filter-Leiste kompakt/einklappbar)."

---

# TEIL K · Übergreifende Features

### K.1 · Einheitliche Navigation
> „Setze auf **allen** Seiten eine **identische Navigationsleiste** ein (Start · Flughäfen · Flugzeuge · Drohnen · Lufträume), gleiches Markup + CSS, aktive Seite hervorgehoben."

### K.2 · „Flugzeugtyp weltweit" (🌍)
> „Baue ein Vollbild-Overlay mit **Weltkarte** (Leaflet, `preferCanvas`), das über `https://api.airplanes.live/v2/type/<ICAO-Typ>` **alle Flugzeuge eines Typs weltweit live** zeigt (A320 ≈ 880). Eingabefeld für den Typcode, Auto-Refresh 30 s, Marker farbcodiert nach Flugphase, ESC schließt. **Sicherheit:** Typcodes auf `[A-Z0-9]` begrenzen, alle Popup-Felder HTML-escapen. Mach es **offen zugänglich** (fester Button in der Leiste) auf Flughäfen- **und** Flugzeug-Seite."

### K.3 · Moderne Animationen
> „Füge **scroll-gekoppelte Animationen** hinzu: native **CSS Scroll-Driven Animations** (`animation-timeline: view()`) für Karten-Reveals, mit **IntersectionObserver als Fallback** für Safari/Firefox, plus dezenten **Hero-Parallax**. `prefers-reduced-motion` respektieren; sicheres Muster, bei dem **nie eine Karte unsichtbar hängen bleibt** (nur JS versteckt beobachtete Elemente kurz)."

---

# TEIL L · Externe Dienste einrichten

### L.1 · OpenAIP-Key (für Lufträume)
1. **openaip.net/register** → kostenloses Konto anlegen (dauert ~1 Min).
2. Im Konto einen **API-Key** erzeugen.
3. **Gewählter Ansatz — eigener Key pro Nutzer:** Der Key wird **nur im Browser** gespeichert (`localStorage`), **nie im Seiten-Code**. Jede\*r trägt den eigenen kostenlosen Key ein (⚙-Panel auf der Lufträume-Seite bzw. 🔑-Button auf der Flughäfen-Seite); ohne Key zeigt die Karte einen Registrierungshinweis. So steckt **kein geteilter Schlüssel** im öffentlichen Code, und nichts läuft über ein fremdes Konto.
   - *Optionale Alternative:* Key serverseitig in einem **Cloudflare Worker** verstecken (Teil L.3) → Karten laufen für alle ohne eigenen Key, dann aber über **ein** Konto.

### L.2 · Groq-Key (für den KI-Assistenten)
1. **console.groq.com** → kostenloses Konto → **API-Key** erstellen (Format `gsk_…`).
2. Diesen Key **nicht** ins HTML schreiben, sondern in den Cloudflare Worker (Teil L.3).

### L.3 · Cloudflare Worker (Schlüssel serverseitig verstecken)
1. **dash.cloudflare.com** → kostenloses Konto → **Workers & Pages** → **Create Worker** → Name z. B. `deploy` → **Deploy**.
2. **Edit code** → den Worker-Code einfügen (die KI liefert ihn; er nimmt Anfragen entgegen und leitet sie mit dem Schlüssel an Groq bzw. OpenAIP weiter, mit CORS-Headern).
3. **Settings → Variables → Add variable** (jeweils „Encrypt"):
   - `GROQ_KEY` = dein Groq-Key
   - `OPENAIP_KEY` = dein OpenAIP-Key
4. **Save & Deploy.** Die Worker-URL (`https://deploy.DEIN-NAME.workers.dev/`) trägst du in den Seiten als `WORKER_URL` bzw. Proxy-Basis ein.
5. **Test:** `…/oaip/airspaces?country=DE&limit=1` im Browser → muss JSON liefern.

> **Prompt dazu:** „Gib mir einen kompletten Cloudflare-Worker (ES-Modul), der 1) POST-Anfragen als Groq-Proxy weiterleitet (Key `env.GROQ_KEY`) und 2) `/oaip/tiles/*` und `/oaip/airspaces` als OpenAIP-Proxy bedient (Key `env.OPENAIP_KEY`), jeweils mit CORS. Erkläre das Deploy im Dashboard."

---

# TEIL M · Automatisierung — Bots via GitHub Actions

Manche Daten (nationale NOTAMs, VFR/IFR-Karten, Länder-Lufträume) ändern sich laufend. Statt sie manuell zu pflegen, holen **Python-Bots** sie automatisch.

> **PROMPT M.1:** „Schreibe **Python-Bots als GitHub Actions**, die alle 6 Stunden aktuelle Daten holen (z. B. DFS-VFR/IFR-Karten, deutsche NfL/NOTAMs, Schweizer Luftraum als GeoJSON) und die Ergebnis-JSONs automatisch ins Repository committen. Die Website liest diese JSONs zur Laufzeit per `fetch`. Achte darauf, dass die Bots **nur Daten-Dateien** ändern, nicht die HTML-Seiten (damit keine Merge-Konflikte mit meiner Arbeit entstehen)."

**So funktioniert eine Action (Kurzform):**
- Datei `.github/workflows/bots.yml` mit `on: schedule: - cron: "0 */6 * * *"`.
- Sie führt die Python-Skripte aus (`python dfs_bot.py` …) und committet die aktualisierten JSONs.
- Geheimnisse (falls nötig) unter **Settings → Secrets and variables → Actions**.

> **Wichtig fürs Teamwork:** Weil die Bots selbst pushen, **immer** vor dem eigenen Push `git fetch` + `git merge origin/main`.

### Die Bot-Architektur konkret (im Projekt: ~30 Bots)
Das Projekt hat **~30 Bots**, gesteuert von **einem** Workflow (`.github/workflows/update-katalog.yml`, alle 6 h):
- **Generischer eAIP-Bot** (`eaip_bot.py`): ein Scraper für **alle Länder mit EUROCONTROL-Standard-eAIP**. Neue Länder werden nur als **Config-Eintrag** in der Liste `LAND_KONFIGS` ergänzt (prefix, name, start_url, output) — **kein neuer Bot nötig**.
- **Spezial-Bots** je Land/Quelle (DFS, FAA, Kanada, China, Russland, Thailand …) für **Nicht-Standard-AIPs** (eigene Portale/Formate).
- Jeder Bot schreibt eine **`<präfix>_katalog_export.json`**; die Website lädt sie über die Zuordnung `KATALOG_DATEI` (Präfix → Datei) und `ladeKatalogDatei()`.

> **PROMPT M.2 — Neues AIP-Land hinzufügen:** „Füge in `eaip_bot.py` einen neuen `LAND_KONFIGS`-Eintrag für **\<Land\>** hinzu (`prefix`, `name`, `start_url` aus dem Quellenkatalog, `mode:'selenium'`, `output:'<prefix>_katalog_export.json'`). Ergänze die Ausgabedatei im Workflow (`git add`) und die Zuordnung `KATALOG_DATEI` in `ourairports.html`, damit die Seite die Daten lädt. Bei Nicht-Standard-AIP stattdessen einen eigenen Länder-Bot nach dem Muster von `belgium_bot.py`."

**Coverage-Hinweis:** Von 208 AIP-Präfixen sind ~120 durch Bots abgedeckt; die restlichen sind überwiegend **login-geschützte oder Nicht-Standard-AIPs** (Naher Osten, Teile Asiens/Afrikas/Lateinamerikas), die einen individuellen Bot bräuchten. Standard-eAIP-Länder lassen sich dagegen in Minuten ergänzen (siehe Prompt M.2).

---

# TEIL N · Sicherheit (Kernthema für die Präsentation)

- Die Seite ist **statisch**: kein Server, keine Datenbank, **kein Login** → nichts zum „Einloggen/Übernehmen".
- Alle Daten-APIs sind **anonyme öffentliche Endpunkte** — laufen über keinen persönlichen Account.
- **Keine Geheimnisse im Client:** schlüsselpflichtige Dienste (OpenAIP, Groq) nutzen den **eigenen Key des Nutzers** (nur im Browser-`localStorage`, nie übertragen) — kein geteilter Schlüssel im Code. *(Alternative: Schlüssel serverseitig im **Cloudflare Worker** verstecken.)*
- **Fremddaten** (aus ADS-B/APIs) vor der Anzeige **HTML-escapen**; Eingaben (z. B. Typcodes) **sanitisieren** → keine Injection.
- Merksatz: *„Der einzige Ort für einen API-Schlüssel ist der Server — nie der Browser."*

> **PROMPT N.1:** „Prüfe den Code auf Sicherheit: escape alle Fremddaten aus APIs vor der Anzeige, sanitisiere Nutzereingaben, und stelle sicher, dass keine Geheimnisse im Client stehen."

---

# TEIL O · Kompletter Datei- & API-Überblick

### Dateien (Auszug)
| Datei | Zweck |
|---|---|
| `index.html` | Startseite mit vier Themen-Karten |
| `ourairports.html` | Flughäfen-Katalog (Suche, Karten, METAR, NOTAM, Infrastruktur, ADS-B, KI) |
| `Luftfahrt_Katalog_*.html` | Flugzeug-Katalog (Muster, ICAO Doc 8643, Triebwerke, Statistik, Tracker, 🌍) |
| `drohnen.html` | UAV-/Drohnen-Datenquellen (einklappbare Gruppen) |
| `luftraeume.html` | OpenAIP-Luftraumkarte |
| `notam.html`, `eurocontrol.html`, `austrocontrol.html` | Zusatz-/Länder-Ansichten |
| `*.json` | von den Bots aktualisierte Exportdaten |
| `*_bot.py` + `.github/workflows/*.yml` | Automatisierung |
| `worker_complete.js` | Cloudflare-Worker (Groq- + OpenAIP-Proxy) |

### APIs (alle browser-tauglich)
| Zweck | Quelle | Key? | CORS |
|---|---|---|---|
| Flughafen-Stammdaten | OurAirports-CSV | nein | ok |
| Live-ADS-B (Umkreis + Typ weltweit) | airplanes.live `/v2/point`, `/v2/type` | nein | `*` |
| ADS-B-Fallback | adsb.lol | nein | `*` |
| Wetter | aviationweather.gov (METAR/TAF) | nein | ok |
| Infrastruktur | OpenStreetMap Overpass-API | nein | ok |
| Geocoding (Ortssuche) | Nominatim (OSM) | nein | ok |
| Lufträume | OpenAIP (`api.core.openaip.net`, Tiles) | **ja** | via Header/Proxy |
| Flugzeug-/Triebwerk-Bilder & -Daten | Wikipedia REST, Wikidata, Wikimedia Commons | nein | `*` (`origin=*`) |
| Registrierungs-Tracker | Flightradar24 (inoffiziell), adsbdb.com | nein | `*` |
| KI-Assistent | Groq (über Cloudflare Worker) | **ja** (im Worker) | via Worker |
| Karten-Bibliothek | Leaflet (CDN) | nein | — |

### Quellensteckbriefe — was · wann verwendet · wie bekommen

Für jede Quelle: **was sie liefert**, **wo/wann sie im Projekt eingesetzt wird**, und **wie man sie bekommt** (Registrierung/Key/Endpunkt). „Wie bekommen" ist bei den meisten schlicht: *öffentlicher Endpunkt, einfach im Code per `fetch` aufrufen — keine Anmeldung.*

**1) OurAirports (Flughafen-Stammdaten)**
- *Liefert:* ~72.000 Flughäfen weltweit (ICAO/IATA, Name, Land, Koordinaten, Typ, Pisten, Frequenzen).
- *Wann/wo:* Flughäfen-Seite, Datengrundlage der Suche (Teil G.1).
- *Wie bekommen:* keine Anmeldung. CSV direkt laden: `https://davidmegginson.github.io/ourairports-data/airports.csv` (+ `runways.csv`, `airport-frequencies.csv`, `navaids.csv`). Kostenlos, Public Domain, CORS ok.

**2) Leaflet (Karten-Bibliothek)**
- *Liefert:* die interaktive Kartenkomponente (Zoom, Marker, Popups).
- *Wann/wo:* überall wo eine Karte ist (Flughäfen, Lufträume, Drohnen, „Typ weltweit").
- *Wie bekommen:* keine Anmeldung. Per CDN einbinden: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js` + `leaflet.css`. Kostenlos (BSD-Lizenz).

**3) OpenStreetMap-Kacheln (Basiskarte)**
- *Liefert:* die Straßenkarten-Kacheln als Kartenhintergrund.
- *Wann/wo:* Hintergrund jeder Leaflet-Karte.
- *Wie bekommen:* keine Anmeldung. Tile-URL `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. Kostenlos; **Attribution Pflicht** („© OpenStreetMap-Mitwirkende").

**4) Esri World Imagery (Satellit)**
- *Liefert:* Satellitenbild-Kacheln (Umschalt-Layer).
- *Wann/wo:* optionaler „Satellit"-Layer in den Karten.
- *Wie bekommen:* keine Anmeldung für den öffentlichen Tile-Endpunkt (`server.arcgisonline.com/.../World_Imagery/...`), Attribution „© Esri".

**5) Overpass-API (OpenStreetMap-Infrastruktur)**
- *Liefert:* Flughafen-Objekte aus OSM (Terminals, Gates, Tower, Betankung, Radar, Navaids).
- *Wann/wo:* Flughafen-Detailkarte, Infrastruktur-Liste (Teil G.5).
- *Wie bekommen:* keine Anmeldung. POST-Abfrage an `https://overpass-api.de/api/interpreter` (mit Spiegelservern als Fallback). Kostenlos; fair use beachten.

**6) Nominatim (Geocoding / Ortssuche)**
- *Liefert:* Ort/Adresse → Koordinaten.
- *Wann/wo:* Ortssuche auf der Lufträume-Karte.
- *Wie bekommen:* keine Anmeldung. `https://nominatim.openstreetmap.org/search?format=json&q=…`. Kostenlos; fair use (kein Massen-Polling).

**7) aviationweather.gov (METAR/TAF)**
- *Liefert:* aktuelles Wetter & Vorhersage je Flughafen.
- *Wann/wo:* Flughafen-Detail (Teil G.3).
- *Wie bekommen:* keine Anmeldung. Öffentliche US-Behörden-API (NOAA/AWC). Kostenlos.

**8) airplanes.live (Live-ADS-B)**
- *Liefert:* aktuell fliegende Flugzeuge — im **Umkreis** (`/v2/point/<lat>/<lon>/<radius>`) und **nach Typ weltweit** (`/v2/type/<ICAO-Typ>`).
- *Wann/wo:* Live-Radar am Flughafen (G.6) und 🌍-„Typ weltweit" (K.2).
- *Wie bekommen:* **keine Anmeldung, kein Key.** Sendet CORS `*` → direkt aus dem Browser nutzbar. Kostenlos.

**9) adsb.lol (ADS-B-Fallback)**
- *Liefert:* dasselbe wie airplanes.live (Ausweichquelle).
- *Wann/wo:* Fallback, falls airplanes.live nicht antwortet.
- *Wie bekommen:* keine Anmeldung, CORS `*`, kostenlos.

**10) Flightradar24 (inoffiziell) — Registrierungs-Tracker**
- *Liefert:* letzte Flüge + Flugzeugdaten zu einer **Registrierung**.
- *Wann/wo:* Flugzeug-Tracker (H.6) und Deep-Link „dieses Flugzeug".
- *Wie bekommen:* keine Anmeldung. Inoffizieller JSON-Endpunkt `api.flightradar24.com/common/v1/flight/list.json?query=<REG>&fetchBy=reg`; sendet CORS `*`. *(Inoffiziell — nur für Lehr-/Demozweck.)*

**11) adsbdb.com (Mode-S / Halterdaten)**
- *Liefert:* Transpondercode (Mode-S), Typ, Halter zu einer Registrierung.
- *Wann/wo:* Tracker (H.6).
- *Wie bekommen:* keine Anmeldung. `https://api.adsbdb.com/v0/aircraft/<REG>`, CORS `*`, kostenlos.

**12) OpenAIP (Lufträume) — ⚠️ braucht Key**
- *Liefert:* Luftraum-Kacheln + klickbare Luftraum-Polygone (Klassen A–G, CTR, TMA, Danger …).
- *Wann/wo:* Lufträume-Karte (Teil J) und Luftraum-Overlays auf anderen Karten.
- *Wie bekommen:* **kostenloses Konto auf `openaip.net/register`** → im Konto einen **API-Key** erzeugen. Nutzung: Header `x-openaip-api-key` (Polygone) bzw. `?apiKey=` (Kacheln). Lizenz CC BY-NC (nicht-kommerziell — für ein Uni-Projekt passend). *Empfehlung:* Key über Cloudflare Worker verstecken (Teil L.3).

**13) Wikipedia REST-API (Bilder & Kurzinfos)**
- *Liefert:* Flugzeug-/Triebwerk-Fotos (`pageimages`, `page/summary`) und Kurztexte.
- *Wann/wo:* Katalog-Karten (H.2), Triebwerke (H.4).
- *Wie bekommen:* keine Anmeldung. `https://en.wikipedia.org/w/api.php?...&origin=*` bzw. `…/api/rest_v1/page/summary/<Titel>`. Kostenlos, CORS via `origin=*`.

**14) Wikidata (strukturierte Daten)**
- *Liefert:* Länge (P2043), Spannweite (P2050), Höhe (P2048), Stückzahl (P1092) u. a.
- *Wann/wo:* Anreicherung der Flugzeugkarten (H.3).
- *Wie bekommen:* keine Anmeldung. Titel → QID über Wikipedia `pageprops`, dann `https://www.wikidata.org/w/api.php?action=wbgetentities&ids=<QID>&props=claims&origin=*`. Kostenlos.

**15) Wikimedia Commons (Foto-Fallback)**
- *Liefert:* echte Fotos, wenn das Wikipedia-Titelbild ein Logo ist.
- *Wann/wo:* Triebwerk-/Flugzeugfotos, wenn Stufe 1 ein Logo liefert (z. B. GE90).
- *Wie bekommen:* keine Anmeldung. `commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&prop=imageinfo&origin=*`. Kostenlos.

**16) Groq (KI-Assistent) — ⚠️ braucht Key (im Worker)**
- *Liefert:* die Antworten des KI-Assistenten (LLM).
- *Wann/wo:* AeroGuide-Chat auf der Flughäfen-Seite (G.8).
- *Wie bekommen:* **kostenloses Konto auf `console.groq.com`** → API-Key (`gsk_…`). Key **nicht** ins HTML, sondern als Variable `GROQ_KEY` in den **Cloudflare Worker** (Teil L.3).

**17) Pollinations.ai (KI-Fallback)**
- *Liefert:* KI-Antworten ohne Key (Ausweich, wenn Groq ausfällt).
- *Wann/wo:* Fallback im KI-Chat.
- *Wie bekommen:* keine Anmeldung. `https://text.pollinations.ai/…`. Kostenlos.

**18) Cloudflare Workers (Secret-Proxy) — Konto nötig**
- *Liefert:* die serverseitige „Zwischenschicht", die Groq-/OpenAIP-Schlüssel versteckt.
- *Wann/wo:* zwischen Website und Groq/OpenAIP.
- *Wie bekommen:* **kostenloses Konto auf `dash.cloudflare.com`** → Worker anlegen, Code einfügen, Variablen `GROQ_KEY`/`OPENAIP_KEY` setzen, deployen (Teil L.3). Kostenloses Kontingent reicht locker.

**19) GitHub Pages (Hosting) — Konto nötig**
- *Liefert:* das kostenlose Webhosting der Seite.
- *Wann/wo:* Veröffentlichung des gesamten Projekts.
- *Wie bekommen:* GitHub-Konto (Teil A.1) → Repo → Settings → Pages aktivieren (Teil C). Kostenlos.

**20) Google Fonts + animate.css (Darstellung)**
- *Liefert:* Schriftart „Inter" bzw. fertige CSS-Animationen.
- *Wann/wo:* Typografie und dezente Animationen auf allen Seiten.
- *Wie bekommen:* keine Anmeldung, per CDN-`<link>`. Kostenlos.

**21) Nationale Luftfahrt-Daten (DFS, Eurocontrol, Austrocontrol, NfL …)**
- *Liefert:* NOTAMs, VFR/IFR-Karten, nationale Luftraumdaten.
- *Wann/wo:* NOTAM-/Länder-Ansichten; werden **nicht** live im Browser geholt, sondern von den **Bots** (Teil M) als JSON/GeoJSON ins Repo geschrieben und dann von der Seite gelesen.
- *Wie bekommen:* öffentliche Behörden-/AIP-Quellen; die Bots laden sie serverseitig in der GitHub Action.

> **Zusammengefasst — „wie bekommt man die Quellen":**
> - **Sofort nutzbar, ohne Anmeldung:** 1–11, 13–15, 17, 20, 21 (öffentliche Endpunkte, einfach per `fetch`).
> - **Kostenloses Konto + Key nötig:** **OpenAIP** (Lufträume) und **Groq** (KI) — beide in ~1 Minute registriert, Key gehört in den **Cloudflare Worker**.
> - **Kostenloses Konto (kein Key im Code):** **GitHub** (Hosting) und **Cloudflare** (Secret-Proxy).

### Zwei Ebenen von Quellen — wichtig zu unterscheiden
Das Projekt nutzt **zwei getrennte Quellen-Ebenen**:

- **Ebene A — Technische Live-APIs** (oben, die 21 Steckbriefe): Was der Browser **zur Laufzeit automatisch abruft** (ADS-B, Wikipedia/Wikidata, Overpass, OpenAIP …). Maschinenlesbar, per `fetch`.
- **Ebene B — Kuratierter Quellenkatalog** (redaktionelle Recherche): Eine **systematisch recherchierte Sammlung offizieller Luftfahrt-Informationsquellen** (nationale AIP je Land, NOTAM-Dienste, Statistik-Quellen …), **von Hand nach einheitlichen Kriterien bewertet**. Das ist die **inhaltliche Grundlage** der Kategorie-Seiten und der eigentliche wissenschaftliche Kern des „Datenkatalogs".

### Ebene B — Der kuratierte Quellenkatalog (Recherche-Methodik)

Jede Quelle wird nach **einheitlichen Kriterien** erfasst und bewertet (die Spalten der Katalog-Tabelle):

| Kriterium | Bedeutung / Beispiel |
|---|---|
| **Name / Betreiber** | z. B. „DFS BasicAIP (Deutschland)", „ASECNA – AIP (17 afrikanische Staaten)" |
| **Inhalt** | was die Quelle enthält, z. B. „AD-2-Karten", „En-Route", „VFR-Karten" |
| **Zielgruppe** | Piloten, Airlines, ANSPs, Behörden, Entwickler … |
| **Format** | PDF, HTML-eAIP, XML (AIXM 5.1), REST/JSON, GeoJSON … |
| **Unique-ID-Schema** | wie Objekte identifiziert werden, z. B. ICAO-Code-Präfix (EDDF), NOTAM-Nummer, FIR-ID |
| **Verfügbarkeit / Login** | öffentlich vs. Login/B2B-Vertrag nötig |
| **AIRAC-Zyklus** | Aktualisierungsrhythmus (28-Tage-AIRAC vs. laufend) |
| **Abdeckung** | geografisch (ein Land, EU/ECAC, weltweit) und inhaltlich (AIP-vollständig?) |
| **Kosten** | kostenlos / Basic kostenlos / kostenpflichtig |
| **Bewertung** | Sterne-Rating (Eignung fürs Projekt) |
| **Link** | direkte Quelle |

**Die 11 recherchierten Fachkategorien — und welcher Bau-Schritt sie nutzt:**

| # | Kategorie | Quellen | Beispiel-Anbieter | Gehört zu Bau-Schritt |
|---|---|---|---|---|
| 1 | **AIP** (national) | 191 Anbieter | DFS BasicAIP, ASECNA (17 Staaten), FAA d-TPP, SkyVector, Eurocontrol EAD | G.4 (NOTAM/AIP-Links je Land) |
| 2 | **NOTAM** | 11 | AVWX, CheckWX, ICAO iSTARS, FAA DINS, autorouter, NOAA | G.4 |
| 3 | **Flugplan** | ca. 11 | Aviation Edge, Cirium, Eurocontrol NM B2B, FAA SWIM, IATA, ICAO Doc 4444/FIXM, Lufthansa API | G.6 / H.6 (Live-Flüge, Tracker) |
| 4 | **Verkehr** | 8 | ADS-B Exchange, OpenSky, FlightAware, Plane Finder, Spire | **G.6** (Live-ADS-B) |
| 5 | **Luftraum** | 9 | OpenAIP, Eurocontrol AIRAC, Open Flightmaps, LXNAV, ChartFox | **Teil J** (Lufträume) |
| 6 | **Flugzeuge** | ca. 11 | ICAO Doc 8643, FAA Registry, EASA Register, Planespotters, SKYbrary, TCDS | **H.1 / H.4** (Katalog, ICAO) |
| 7 | **Triebwerke** | 11 | CFM, GE, Pratt & Whitney, Rolls-Royce, Safran, Honeywell, ICAO EEDB, TCDS | **H.4** (Triebwerke) |
| 8 | **Technische Infos** | 18 | CS-25 / CS-E, FAR 25/33, RTCA DO-178C / DO-160, Jane's, NASA | Katalog „Technische Infos" |
| 9 | **Wetter** | 24 | AWC/NOAA (METAR/TAF/SIGMET), ECMWF, Meteoblue, Meteomatics, DWD, GAFOR, SkySight | **G.3** (Wetter) |
| 10 | **Statistik** | 15 | Eurostat, DESTATIS, ICAO WATS, IATA, Boeing/Airbus Forecast, NTSB, ASN | **H.5** (Statistik-Dashboard) |
| 11 | **UAVs / Drohnen** | 17 (Code: 18) | OpenAIP UAV, DJI FlySafe, Dronetag, EASA/LBA/DFS/Dipul, Drone-Check | **Teil I** (Drohnen) |

*(Zähler laut Recherche-Tabelle; „ca." = in der Vorlage nicht eindeutig lesbar. Die vollständige Liste aller **229 bewerteten Quellen** liegt in **`QUELLENKATALOG.csv`**; Zählungen & Methodik in **`QUELLENKATALOG.md`**.)*

> **➜ Web-Ansicht des Quellenkatalogs (öffentlich):** [Luftfahrt-Datenkatalog — alle 229 Quellen mit Bewertung](https://jscepik-source.github.io/luftfahrtdatenkatalog/quellenkatalog.html)

**So verbindet sich Recherche und Bau:** Vor dem Bau einer Seite steht die **Recherche der passenden Kategorie** (z. B. „Wetter": 24 Quellen vergleichen und bewerten). Beim Bauen wird dann entweder die **beste browser-taugliche Quelle als Live-Feature** umgesetzt (Wetter → aviationweather.gov, Verkehr → airplanes.live) **oder die kuratierte, bewertete Quellenliste** als filterbare Katalog-Seite gerendert (AIP, Flugzeuge, Triebwerke, Statistik, Drohnen). **Merke:** erst recherchieren & bewerten, dann bauen — nicht umgekehrt.

**Wie der Katalog in die Website kommt:**
Die bewerteten Quellen werden als **Datenobjekte im JavaScript** hinterlegt (im Projekt die `src(...)`-Einträge je Kategorie-Seite: Bewertungszahlen, Name, Inhalt, Zielgruppe, Format, Bemerkung, Link). Die Seite **rendert daraus automatisch** die aufklappbaren Quellen-Karten mit Sterne-Bewertung, Filtern und Suche. So wird aus der Recherche-Tabelle eine interaktive, filterbare Katalog-Seite.

### Prompts — den Quellenkatalog in die Website einbauen (Schritt für Schritt)

So wird aus der Recherche-Tabelle eine **interaktive, filterbare Katalog-Seite**. Prompts der Reihe nach:

> **Prompt B.1 — Tabelle → Daten:** „Ich habe eine Tabelle mit Luftfahrt-Quellen (Spalten: Kategorie, Name, Inhalt, Zielgruppe, Format, Unique-ID-Schema, Verfügbarkeit/Login, AIRAC-Zyklus, Abdeckung, Kosten, Bewertung 1–5, URL, Bemerkung). Wandle sie in ein **JavaScript-Datenarray** um — pro Quelle ein Objekt mit diesen Feldern. Bei vielen Einträgen lagere sie stattdessen in eine externe **`quellen.json`** aus, die die Seite per `fetch` lädt."

> **Prompt B.2 — Katalog-Seite rendern:** „Baue eine **Kategorie-Seite**, die dieses Array rendert: pro Quelle eine **aufklappbare Karte** mit Name, **Sterne-Bewertung**, Kurzinfo und Detailfeldern (Zielgruppe, Format, Verfügbarkeit, AIRAC, Abdeckung, Kosten, Bemerkung) sowie einem **‚Zur Quelle ↗'-Button**. Oben **Filter-Chips** (nach Kategorie / Format / Kosten / maschinenlesbar), eine **Suche** und ein **Ergebniszähler**. Gruppiere nach Kategorie mit **einklappbaren Abschnitten**."

> **Prompt B.3 — Bewertung & Sortierung:** „Berechne die **Sterne-Bewertung** als Mittel der Einzelkriterien und zeige sie als halbe/volle Sterne. Ergänze eine Sortier-Option **‚Beste Bewertung zuerst'** und **‚Kostenlos zuerst'**."

> **Prompt B.4 — AIP/NOTAM je Land (Präfix-Zuordnung):** „Für AIP- und NOTAM-Quellen: lege eine Zuordnung **ICAO-Präfix → {Name, URL}** an (z. B. `'ED'` → DFS, `'LF'` → SIA France). Zeige auf **jeder Flughafen-Detailkarte automatisch** den passenden AIP-/NOTAM-Link anhand des ICAO-Präfixes des Flughafens."

> **Prompt B.5 — Kennzahlen aus den Daten:** „Berechne aus dem Quellen-Array **automatisch Kennzahlen** (Anzahl je Kategorie, Anteil kostenlos, Anteil maschinenlesbar) und zeige sie als **Chip-Zähler** und kleine **CSS-Balkendiagramme** — so bleibt die Statistik automatisch korrekt, wenn Quellen dazukommen."

> **Prompt B.6 — Einbinden & Verlinken:** „Verlinke die neue Quellen-Kategorie in der **einheitlichen Navigationsleiste** und als **Karte auf der Startseite**. Setze konsistentes Design (gleiche Karten-/Chip-Stile wie die übrigen Seiten)."

> **Prompt B.7 — Pflege über CSV (empfohlen bei großen Katalogen):** „Ich pflege die Quellen in **`QUELLENKATALOG.csv`**. Lies die CSV im Browser per `fetch`, **parse** sie (einfacher CSV-Parser) und rendere daraus die Katalog-Seite — so ändere ich nur die CSV, die Seite bleibt automatisch aktuell. Optional: ein **GitHub-Actions-Bot**, der die CSV regelmäßig aus einer Google-Tabelle neu erzeugt und committet."

> **Prompt B.8 — Verknüpfung mit Live-Daten:** „Wo eine recherchierte Quelle eine **CORS-freie API** hat (z. B. Wetter, ADS-B), setze sie zusätzlich als **Live-Feature** um und verlinke von der Quellen-Karte direkt dorthin (‚Live ansehen')."

**Didaktischer Wert (für die Bewertung):** Ebene B zeigt **systematische, kriteriengeleitete Quellenrecherche** — nicht nur „Daten anzeigen", sondern Quellen **vergleichen und bewerten**. Das ist der wissenschaftliche Kern des Projekts; Ebene A (die Live-APIs) ist die technische Umsetzung.

---

# TEIL P · Fehlerbehebung (Troubleshooting)

| Symptom | Ursache | Lösung |
|---|---|---|
| Änderung nicht live | GitHub-Pages-Cache | 1–2 Min warten, dann **Strg+F5** (Hard-Reload) |
| `git push` abgelehnt | Bots haben zwischenzeitlich gepusht | `git fetch` + `git merge origin/main`, dann erneut pushen |
| Karte/Bild lädt nicht | API blockt (CORS/Rate-Limit/404) | Fallback prüfen; anderen Endpunkt/Proxy nutzen; Bild-Fallback über Wikipedia-REST |
| Flugzeugbild ist ein Logo | Wikipedia-Titelbild ist Firmenlogo | Logo-Filter + **Wikimedia-Commons-Fallback** |
| Terminal fehlt (z. B. EDDF T2) | in OSM nur `building=terminal` getaggt | Overpass-Abfrage um `building=terminal` erweitern |
| Lufträume leer | OpenAIP-Key fehlt/ungültig | Key eintragen (Teil L.1) bzw. Worker deployen |
| 🌍 nicht sichtbar | erschien früher nur bei Live-Verkehr | fester Button in der Leiste (Teil K.2) |
| Karten „springen"/unsichtbar | Animations-Zustand | sicheres Reveal-Muster (nur JS versteckt beobachtete Elemente) |

> **Bester Fehler-Prompt:** „Bei **[konkretes Beispiel]** passiert **[was]** statt **[erwartet]**. Hier der Konsolen-Fehler: **[Text]**. Bitte Ursache finden und beheben."

---

# TEIL Q · Der gesamte Ablauf als Checkliste

**Setup (einmal):**
- [ ] GitHub-Konto, Git, VS Code, KI-Assistent installiert
- [ ] Repo erstellt, geklont, **GitHub Pages** aktiviert
- [ ] Test-`index.html` live gesehen (commit→push→Browser)
- [ ] Projektrahmen-Prompt (E.0) gesetzt

**Seiten bauen (jeweils: Prompt → im Browser prüfen → commit → push):**
- [ ] Startseite (F.1, F.2)
- [ ] Flughäfen G.1 → G.8 (Suche, Karte, Wetter, NOTAM, Infrastruktur, ADS-B, Deep-Links, KI)
- [ ] Flugzeuge H.1 → H.7 (Gerüst, Fotos, Wikidata, ICAO/Triebwerke, Statistik, Tracker, 🌍)
- [ ] Drohnen (Teil I)
- [ ] Lufträume (Teil J)

**Übergreifend:**
- [ ] Einheitliche Navigation (K.1)
- [ ] „Typ weltweit" 🌍 (K.2)
- [ ] Moderne Animationen (K.3)

**Dienste & Automatisierung:**
- [ ] OpenAIP-Key (L.1), Groq-Key (L.2), Cloudflare Worker (L.3)
- [ ] Bots als GitHub Actions (Teil M)

**Abschluss:**
- [ ] Sicherheits-Durchgang (Teil N)
- [ ] Alles live geprüft; Doku (`VERBESSERUNGEN_Praesentation.md`) aktualisiert

---

## Kernbotschaft für die Lehre
Der Weg von Null zu dieser Website ist **kein einzelner Riesen-Prompt**, sondern **viele kleine, geprüfte Schritte**: Rahmen setzen → Feature bauen → im Browser prüfen → Fehler mit konkretem Beispiel melden → nachbessern → committen. Die KI liefert den Code; **Zielklarheit, richtige Datenquellen und Prüfen** liefert der Mensch.

*Ergänzt die technische Ergebnis-Übersicht in `VERBESSERUNGEN_Praesentation.md`. Die lückenlose reale Zeitleiste steht in der Git-Commit-Historie (`git log`).*
