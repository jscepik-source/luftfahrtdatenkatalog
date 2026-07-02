# Anleitung: Eine datengetriebene Luftfahrt-Website mit KI bauen
### Vollständige Prompt- und Vorgehens-Dokumentation
**Projekt:** Luftfahrtdatenkatalog · Hochschule RheinMain · Modul Avionik
**Art:** Statische Single-Page-Webanwendung auf GitHub Pages (nur HTML/CSS/JavaScript, kein Backend)
**Zweck dieses Dokuments:** Nachvollziehbare Schritt-für-Schritt-Anleitung, wie die Website mit Hilfe einer KI (Claude / vergleichbar) entwickelt wurde — inkl. der verwendeten Prompts.

---

## Inhaltsverzeichnis
0. Methodik & Werkzeuge
1. Projektrahmen (Meta-Prompt)
2. Startseite
3. Flughäfen-Seite (Kernstück)
4. Flugzeug-Katalog
5. Drohnen-Seite
6. Lufträume-Karte
7. Übergreifende Features (Navigation, Animationen, Statistik, Sicherheit)
8. Automatisierung (GitHub Actions / Bots)
9. Deployment (GitHub Pages)
10. Iteration & Fehlerbehebung — echte Prompts aus der Entwicklung
11. Prinzipien des Promptens (didaktische Zusammenfassung)
12. Anhang: Authentische Prompt-Beispiele (im Original-Wortlaut)

---

## 0 · Methodik & Werkzeuge

### Grundidee der KI-gestützten Entwicklung
Die Website wurde **nicht** in einem Rutsch erzeugt, sondern **iterativ**: ein Grundgerüst, dann Feature für Feature, jeweils mit Prüfen, Nachbessern und Fehlerbehebung. Die KI schreibt den Code, der Mensch gibt Ziel, Kontext, Datenquellen und Qualitätskriterien vor und prüft das Ergebnis.

### Werkzeuge
- **KI-Coding-Assistent** (Claude Code / Cursor / VS-Code-Erweiterung) — schreibt und ändert Dateien direkt im Projekt.
- **Editor + Browser** — zum Prüfen jeder Änderung.
- **Git + GitHub** — Versionskontrolle; **GitHub Pages** als kostenloses Hosting.
- **Keine** Frameworks, **kein** Build-Schritt: reines HTML/CSS/JavaScript (Vanilla), damit alles direkt auf GitHub Pages läuft.

### Die vier Grundprinzipien (wurden bei fast jedem Prompt mitgegeben)
1. **Statisch & serverlos** — kein Backend, keine Datenbank; jede Seite ist eine eigenständige `.html`-Datei.
2. **Nur CORS-freie, öffentliche APIs** — die direkt aus dem Browser funktionieren.
3. **Robustheit** — jede Funktion mit Fallback und Fehlerbehandlung.
4. **Sicherheit** — Fremddaten escapen, keine Geheimnisse im Client-Code.

---

## 1 · Projektrahmen (Meta-Prompt)

Dieser Prompt wird **einmal zu Beginn** gesetzt und definiert den Rahmen für alles Weitere:

> **Prompt 1.1 — Projektkontext**
> „Ich baue ein studentisches Uni-Projekt (Hochschule RheinMain, Modul Avionik): einen weltweiten **Luftfahrtdatenkatalog** als **statische Website** für **GitHub Pages** — nur HTML/CSS/JavaScript, **kein Backend, keine Datenbank, kein Build-Tool**. Jede Seite ist eine einzelne, in sich geschlossene `.html`-Datei mit eingebettetem CSS und JavaScript (Vanilla, keine Frameworks). Nutze ausschließlich **kostenlose, CORS-freie öffentliche APIs**, die direkt aus dem Browser funktionieren. Schreibe sauberen, kommentierten Code und baue jede Funktion mit **Fallback/Fehlerbehandlung**. Sag mir bei jeder API vorab, ob sie ohne Key und mit CORS funktioniert. Design: modern, clean, responsive, Dark-Mode."

---

## 2 · Startseite (`index.html`)

> **Prompt 2.1**
> „Baue eine `index.html` als **Themen-Auswahlseite** mit vier großen anklickbaren Karten: **Flughäfen, Flugzeuge, Drohnen, Lufträume**. Hero-Bereich mit Farbverlauf, responsive Grid, Dark-Mode über `prefers-color-scheme`, Icons als Inline-SVG, Hover-Effekte, Footer mit Impressum-Link."

> **Prompt 2.2 — Verfeinerung**
> „Füge eine sanfte, gestaffelte Einblende-Animation beim Laden hinzu (Hero + Karten faden nacheinander ein). `prefers-reduced-motion` respektieren."

**Ergebnis/Technik:** CSS-Grid, CSS-Custom-Properties für das Farbschema, `@keyframes` mit gestaffelten `animation-delay`.

---

## 3 · Flughäfen-Seite (`ourairports.html`) — Kernstück

Diese Seite entstand in vielen Schritten. Reihenfolge:

> **Prompt 3.1 — Datengrundlage & Suche**
> „Baue `ourairports.html`: einen durchsuchbaren Katalog von **~72.000 Flughäfen weltweit** aus dem **OurAirports-CSV** (`ourairports.com/data/`). Sofort-Suche nach ICAO, IATA, Name, Stadt, Land. Ergebnisliste mit **Infinite-Scroll** (batchweise nachladen, ~50 pro Batch). Filter-Chips nach Flughafentyp; Kontinent-Auswahl."

> **Prompt 3.2 — Detailkarte je Flughafen**
> „Mach jeden Treffer aufklappbar mit Detailansicht: **Leaflet-Karte** (OpenStreetMap + optional Satellit), Pisten (Länge/Belag/ILS), Frequenzen, Elevation, Koordinaten und externe Links (SkyVector, Google Maps, ChartFox)."

> **Prompt 3.3 — Wetter & NOTAMs**
> „Ergänze **Live-METAR und TAF** (Quelle: aviationweather.gov) mit dekodierter Darstellung, sowie Links zu nationalen **NOTAM/AIP**-Quellen (DFS, Eurocontrol, Austrocontrol …)."

> **Prompt 3.4 — Infrastruktur aus OpenStreetMap**
> „Lade pro Flughafen die **Infrastruktur aus OpenStreetMap** über die **Overpass-API**: Terminals, Gates, Tower, Betankung, Radar sowie Navaids (ILS/VOR/NDB/DME). Zeichne sie auf die Karte und liste sie kategorisiert auf. Nutze Overpass-Spiegelserver als Fallback."

> **Prompt 3.5 — Live-ADS-B-Radar**
> „Baue ein **Live-ADS-B-Radar**: hole aktuelle Flugzeuge im Umkreis eines Flughafens von **`api.airplanes.live/v2/point/<lat>/<lon>/<radius>`** (CORS-frei, kein Key). Zeige sie als drehbare Flugzeug-Marker auf der Leaflet-Karte mit **flüssiger 60-fps-Animation per Dead-Reckoning** (zwischen den Updates entlang Kurs+Geschwindigkeit weiterrechnen). Zusätzlich eine Live-Flugliste: Callsign, Kennzeichen, Typ, Höhe, Geschwindigkeit, Flugphase (farbcodiert)."

> **Prompt 3.6 — KI-Assistent**
> „Baue einen KI-Chat-Assistenten ('AeroGuide'), der Fragen zur Luftfahrt und zum aktuellen Kontext beantwortet. Der API-Schlüssel darf **nicht** im Client stehen — leite die Anfrage über einen **Cloudflare Worker** (serverseitig, Schlüssel als Umgebungsvariable). Baue Fallback-Anbieter ein, falls der Hauptanbieter ausfällt."

---

## 4 · Flugzeug-Katalog (`Luftfahrt_Katalog_*.html`)

> **Prompt 4.1 — Grundgerüst**
> „Baue einen Flugzeug-Katalog: Datenobjekt im JavaScript mit Flugzeugmustern (Name, Hersteller, Erstflug, technische Daten, Bewertung). Kategorien, Filter-Chips, Suche, aufklappbare Detailkarten mit dezenter Einblende-Animation."

> **Prompt 4.2 — Fotos automatisch laden**
> „Lade die **Fotos automatisch von Wikipedia** (`api/rest_v1/page/summary/<Titel>` bzw. `pageimages`). **Wichtig:** Viele Wikimedia-`thumb`-URLs liefern HTTP 400 — baue einen **Fallback**, der bei Bildfehler ein funktionierendes Thumbnail über die Wikipedia-REST-API nachlädt. **Filtere Firmenlogos** heraus; ist das Titelbild ein Logo, hole stattdessen ein echtes Foto aus **Wikimedia Commons** (`generator=search`, Dateien-Namespace)."

> **Prompt 4.3 — Daten aus Wikidata**
> „Reichere jede Flugzeugkarte beim Aufklappen mit **strukturierten Daten aus Wikidata** an: Wikipedia-Titel → QID (`pageprops`) → Eigenschaften (`wbgetentities`): Länge (P2043), Spannweite (P2050), Höhe (P2048), Stückzahl (P1092). Nur zuverlässige Einheiten (Meter/Anzahl). Bereits kuratierte Werte haben Vorrang (keine widersprüchlichen Doppelangaben). Alles CORS-frei via `origin=*`."

> **Prompt 4.4 — ICAO Doc 8643 & Triebwerke**
> „Baue eine **ICAO-Doc-8643-Ansicht** (Liste aller Typencodes mit Klasse/Triebwerk) und eine **Triebwerks-Ansicht**. Ergänze **jedes Triebwerk mit Foto** (Wikipedia-Suche → Foto; Logo-Filter; bei Logo → Wikimedia-Commons-Fallback)."

> **Prompt 4.5 — Statistik-Dashboard**
> „Werte die Statistik-Seite auf: statt nur Quellen-Links ein **Dashboard mit echten Diagrammen**, live aus den Katalog-Daten berechnet (Flugzeuge nach Jahrzehnt, Top-Hersteller, Triebwerke nach Typ) plus Kennzahlen. **Pure CSS/SVG-Balken, keine Chart-Bibliothek**, mit Wachstums-Animation; `prefers-reduced-motion` beachten."

> **Prompt 4.6 — Live-Tracker**
> „Baue einen Tracker: Nutzer gibt eine **Registrierung** ein und bekommt **letzte Flüge + Mode-S-Transpondercode + Flugzeugdaten**. Quellen, die aus dem Browser funktionieren: Flightradar24 (inoffiziell, `flight/list.json?query=<REG>&fetchBy=reg`) und adsbdb.com. Beide senden CORS `*`."

---

## 5 · Drohnen-Seite (`drohnen.html`)

> **Prompt 5.1**
> „Baue `drohnen.html`: eine Marktübersicht von **UAV-/Drohnen-Datenquellen** (Datenobjekt im JS), gruppiert nach Kategorie (Tracking/Remote-ID, Geo-Zonen, Regeln, Behörden, Wetter, NOTAMs). Filter-Chips, Suche, aufklappbare Detailkarten. Für Karten-Quellen eine kleine Leaflet-Karte mit OpenAIP-Lufträumen."

> **Prompt 5.2 — Interface verbessern**
> „Überarbeite die Drohnen-Seite: prüfe auf Fehler, verbessere das Interface. Konkret: Barrierefreiheit (Screenreader-Label war unsichtbar definiert), **datengetriebene Kennzahlen und Chip-Zähler** (aus den Daten berechnet, bleiben automatisch korrekt), sichtbarer Tastatur-Fokus."

> **Prompt 5.3 — Einklappbare Kategorien**
> „Mach die Kategorie-Gruppen **einklappbar** (Überschrift zum Auf-/Zuklappen), damit man die Liste kompakt überblicken kann."

---

## 6 · Lufträume-Karte (`luftraeume.html`)

> **Prompt 6.1**
> „Baue `luftraeume.html`: eine **Vollbild-Leaflet-Weltkarte** der Lufträume (ICAO-Klassen A–G, CTR, TMA, Restricted/Prohibited/Danger) auf Basis von **OpenAIP** (Kachel-Layer + klickbare Polygone via `api.core.openaip.net`). Filter nach Land, Typ und ICAO-Klasse. Farbcodierte Legende, Ortssuche via Nominatim."

> **Prompt 6.2 — Modernisieren**
> „Modernisiere die Optik (einheitliche Schrift, weiche Schatten, Pill-Filter, sanfte Einblendungen), mach die **Legende einklappbar** und die **Karte möglichst groß** (Filter-Leiste kompakt/einklappbar halten)."

*(Zum OpenAIP-Schlüssel siehe Kapitel 7 · Sicherheit — hier wurde bewusst die Abwägung „Einfachheit vs. Sicherheit" thematisiert.)*

---

## 7 · Übergreifende Features

> **Prompt 7.1 — Einheitliche Navigation**
> „Setze auf **allen** Seiten eine **identische Navigationsleiste** ein (Start · Flughäfen · Flugzeuge · Drohnen · Lufträume) — gleiches Markup und CSS, aktive Seite hervorgehoben."

> **Prompt 7.2 — „Flugzeugtyp weltweit"**
> „Baue eine Funktion, die **jeden Flugzeugtyp weltweit live** auf einer Weltkarte zeigt: Vollbild-Overlay mit Leaflet (`preferCanvas` für tausende Marker), Daten von **`api.airplanes.live/v2/type/<ICAO-Typ>`** (z. B. A320 ≈ 880 weltweit), Auto-Refresh 30 s, Marker farbcodiert nach Flugphase. **Sicherheit:** Typcodes auf `[A-Z0-9]` begrenzen, alle Popup-Felder HTML-escapen. Mach das Feature **offen zugänglich** (fester Button in der Leiste) und integriere es sowohl auf der Flughäfen- als auch auf der Flugzeug-Seite (🌍-Chip an jedem Typencode)."

> **Prompt 7.3 — Moderne Animationen**
> „Füge **moderne, scroll-gekoppelte Animationen** hinzu: native **CSS Scroll-Driven Animations** (`animation-timeline: view()`) für Karten-Reveals, mit **IntersectionObserver als Fallback** für Safari/Firefox, plus dezenten **Hero-Parallax**. `prefers-reduced-motion` respektieren; ein sicheres Muster verwenden, bei dem **nie eine Karte unsichtbar hängen bleibt** (nur JS versteckt beobachtete Elemente kurzzeitig)."

> **Prompt 7.4 — Sicherheit / API-Schlüssel**
> „Der OpenAIP-Schlüssel steht im öffentlichen Client-Code. Erkläre mir das Risiko und die zwei sauberen Optionen:
> (a) **Cloudflare-Worker als Proxy** — Schlüssel als verschlüsselte Umgebungsvariable, die Seiten rufen den Worker statt OpenAIP direkt; Schlüssel nirgends sichtbar.
> (b) **Direkter, kostenloser Read-only-Schlüssel** im Client für sofortigen Betrieb.
> Gib mir den vollständigen Worker-Code und beschreibe den Deploy. Härte außerdem den restlichen Code (Fremddaten escapen, Eingaben sanitisieren)."

---

## 8 · Automatisierung (GitHub Actions / Bots)

> **Prompt 8.1**
> „Schreibe **Python-Bots als GitHub Actions**, die alle 6 Stunden aktuelle Daten holen (z. B. DFS-VFR/IFR-Karten, NOTAMs, nationale Luftraumdaten) und die Ergebnis-JSONs automatisch ins Repository committen. Die Website liest diese JSONs zur Laufzeit. Achte darauf, dass die Bots nur Daten-Dateien ändern, nicht die HTML-Seiten."

---

## 9 · Deployment (GitHub Pages)

> **Prompt 9.1**
> „Erkläre mir Schritt für Schritt, wie ich das Projekt über **GitHub Pages** veröffentliche (Repository, `main`-Branch, Pages-Einstellung), und wie ich Änderungen sicher pushe, obwohl die Bots regelmäßig selbst committen (erst `git fetch` + `merge`, dann pushen)."

---

## 10 · Iteration & Fehlerbehebung — echte Prompts aus der Entwicklung

Ein zentraler Teil der Arbeit ist **Nachbessern**. Beispiele echter Prompts (leicht geglättet), die zeigen, wie man iterativ verbessert:

- **Verknüpfung herstellen:** „Wenn ich im Live-Radar auf den **Flugzeugtyp** klicke, soll im Katalog **nur die passende Typ-Karte** aufgehen; klicke ich auf das **Kennzeichen**, soll **nur der Live-Tracker** dieses Flugzeugs erscheinen."
- **Bug melden mit Beispiel:** „Die **Kennnummer** der Flugzeuge kann ich nicht anklicken." → (Ursache: war reiner Text, nicht verlinkt.)
- **Datenlücke mit konkretem Fall:** „Warum gibt es bei **EDDF kein Terminal 2** in der Infrastruktur?" → (Ursache: in OSM nur als `building=terminal` getaggt → Abfrage erweitert.)
- **Fehlendes Bild mit Beispiel:** „Das **GE90-Bild** fehlt." → (Ursache: Wikipedia-Titelbild war ein Logo → Commons-Fallback ergänzt.)
- **Mehr Daten:** „Ergänze pro Flugzeug **so viele Daten wie möglich** (Baujahr, Größe, Passagierzahl, Zweck …)." → (Lösung: kuratierte Kernwerte + Wikidata-Anreicherung.)
- **Design/UX:** „Kannst du **moderne Scroll-Animationen** einbauen, wie in ganz modernen Seiten?" → (Lösung: `animation-timeline: view()` + Fallback.)
- **Zusammenarbeit/Merge:** „Mein Kommilitone hat die Seite verändert (einklappbare Filter), ohne es mir zu sagen — behalte seinen Filter, aber übernimm sonst alle meine Änderungen." → (Lösung: gezielter Merge beider Stände.)
- **Sicherheitswunsch:** „Ich will nicht, dass man die Seite hacken kann / dass Daten über meinen Account laufen." → (Lösung: Aufklärung + Härtung + Worker-Proxy als Option.)

**Lernpunkt für die Lehre:** Gute Fehler-Prompts enthalten **ein konkretes Beispiel** (welcher Flughafen, welches Flugzeug, welcher Klick) — damit findet die KI die Ursache viel schneller.

---

## 11 · Prinzipien des Promptens (didaktische Zusammenfassung)

1. **Rahmen einmal klar setzen** (statisch, CORS-frei, kein Backend) — spart bei jedem Folge-Prompt Erklärungen.
2. **Klein & iterativ** statt „bau mir alles" — erst Gerüst, dann Feature für Feature.
3. **Datenquellen konkret vorgeben** — „nutze `airplanes.live/v2/type`, CORS-frei". Sonst rät die KI oft nicht funktionierende Endpunkte.
4. **Immer nach Fallbacks fragen** — „was, wenn die API/das Bild scheitert?".
5. **Sicherheit explizit fordern** — Fremddaten escapen, keine Secrets im Client.
6. **Fehler mit konkretem Beispiel melden** — Flughafen/Flugzeug/Klick nennen, idealerweise Konsolen-Log.
7. **Design-Kriterien mitgeben** — modern, clean, responsive, Dark-Mode, dezente Animationen, Barrierefreiheit.
8. **Nach jedem Schritt prüfen** — im Browser testen, dann erst weiter.
9. **Robustheit vor Schönheit** — lieber eine Funktion mit sauberem Fallback als fünf ohne.

---

## 12 · Anhang: Authentische Prompt-Beispiele (Original-Wortlaut)

Zur Veranschaulichung, wie Prompts in der Praxis tatsächlich formuliert wurden (bewusst unpoliert — die KI kommt auch mit knappen, umgangssprachlichen Anweisungen zurecht, wenn der Rahmen einmal steht):

- „ich will wenn ich auf den flugzeug typ klicke, dass ich direkt die infos nur über den typ angezeigt bekomme, und wenn ich auf den icao code des flugzeugs drücke, will ich die historie [Flüge] und die infos über das flugzeug."
- „und die einzelnen flugzeuge, daten so viele wie möglich hinzufügen, wie baujahr, größe, passagieranzahl, zweck etc."
- „kannst du auch sowas einfügen [Scroll-Animation wie WOW.js] … also diese animation dinger."
- „kannst du auch scroll down animationen machen, wie in den ganz modernen sachen."
- „bitte alle triebwerke mit foto ergänzen."
- „statistik verbessern."
- „kannst du besser offener integrieren und das auch bei der flugzeug seite reinholen."

**Fazit:** Entscheidend ist nicht die perfekte Formulierung, sondern **klarer Rahmen + konkretes Ziel + konkretes Beispiel + iteratives Prüfen**.

---

*Erstellt als Lehr-/Vorführmaterial für das Modul Avionik. Ergänzt die technische Übersicht in `VERBESSERUNGEN_Praesentation.md`.*
