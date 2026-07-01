# Luftfahrtdatenkatalog — Verbesserungen & Weiterentwicklung
### Dokumentation für die Präsentation · Hochschule RheinMain · Avionik
**Projekt:** Weltweiter Luftfahrtdatenkatalog (GitHub Pages, Single-Page-Webanwendung)
**Repository:** github.com/jscepik-source/dfs-katalog · **Live:** jscepik-source.github.io/dfs-katalog
**Stand der Überarbeitung:** Juni 2026 (18 Commits)

---

## 0. Überblick auf einen Blick

Die Überarbeitung umfasst **fünf Themenblöcke**:

| # | Block | Kernnutzen |
|---|-------|-----------|
| 1 | **Verknüpfte Datenansichten** (Deep-Links) | Ein Klick führt gezielt vom Flughafen zum passenden Flugzeug/Typ |
| 2 | **Live-ADS-B-Erweiterung** | Flugzeugtyp weltweit live auf der Karte verfolgen |
| 3 | **Datenqualität** | Mehr Flugzeugdaten (Wikidata), korrekte Bilder, vollständigere Terminals |
| 4 | **Sicherheit & Architektur** | API-Schlüssel serverseitig versteckt (Cloudflare-Worker-Proxy) |
| 5 | **UI/UX & moderne Animationen** | Einheitliche Navigation, scroll-gekoppelte Animationen (Apple-Stil) |

---

## 1. Verknüpfte Datenansichten (Cross-Page-Deep-Links)

**Problem:** Flughafen-, Flugzeug- und Live-Radar-Daten lagen auf getrennten Seiten ohne gezielte Verknüpfung.

**Lösung — kontextbezogene Fokus-Ansichten:**
- **Klick auf einen Flugzeug*typ*** (z. B. „Airbus A320" im Live-Radar) → öffnet im Flugzeug-Katalog **nur die eine passende Typ-Karte**, direkt aufgeklappt.
- **Klick auf das *Kennzeichen*** eines Flugzeugs (z. B. „D-AIMA") → öffnet **nur den Live-Tracker** mit Flughistorie (letzte Flüge) + Flugzeugdaten + Mode-S-Transpondercode.
- Eine **Fokus-Leiste** mit Button „Alle Flugzeuge anzeigen" führt zurück zur Vollansicht.

**Technisch:** URL-Parameter (`?q=Modell`, `?reg=Kennung`), CSS-Attribut-Selektoren (`[data-focus]`) zum gezielten Ein-/Ausblenden, Token-Abgleich zur Zuordnung des Live-Musters auf das Katalog-Basismodell.

**Zusätzlich:** Das **Kennzeichen ist in den Live-Fluglisten jetzt anklickbar** (vorher nur reiner Text) → direkter Sprung zum Live-Tracker.

---

## 2. Live-ADS-B-Erweiterung: „Flugzeugtyp weltweit"

**Neue Funktion:** Über ein 🌍-Symbol lässt sich **jeder Flugzeugtyp weltweit live** auf einer eigenen Weltkarte anzeigen (z. B. „alle A320, die gerade weltweit fliegen").

**Datenquelle:** `airplanes.live/v2/type/<ICAO-Typ>` — liefert alle aktuell per ADS-B erfassten Flugzeuge eines Typs (A320 ≈ 880, B738 ≈ 1.200 weltweit).
- **CORS-frei** → direkt aus dem Browser nutzbar, kein Server nötig.
- **Performance:** Canvas-basierte Marker (Leaflet `preferCanvas`) für tausende Punkte flüssig.
- **Auto-Refresh** alle 30 s, farbcodiert nach Flugphase (Reise/Steig/Sink/Boden).

**Sicherheit (Security-Hardening):** Typ-Codes werden auf `[A-Z0-9]` begrenzt und alle Popup-Felder HTML-escaped → keine Injection über manipulierte ADS-B-Daten möglich.

---

## 3. Datenqualität

### 3a. Mehr Daten pro Flugzeug
- **Sofort sichtbar:** Erstflug, Hersteller, Zulassung sowie kuratierte Kernwerte (Zweck, Länge, Höhe, Reichweite, Passagierzahl, Triebwerke) für die bekanntesten Muster.
- **Automatisch angereichert:** Beim Aufklappen einer Karte werden **Länge, Spannweite, Höhe und Stückzahl live von Wikidata** nachgeladen (Wikipedia → Wikidata-QID → strukturierte Eigenschaften, CORS-frei). Bereits kuratierte Werte haben Vorrang (keine widersprüchlichen Doppelangaben).

### 3b. Fehlende & falsche Flugzeugbilder behoben
- **Fehlerhafte Bild-URLs:** Viele Wikimedia-`thumb`-Links liefern HTTP 400 (Hotlink-/Bot-Schutz). → **Fallback** lädt bei Bildfehler automatisch ein funktionierendes Thumbnail über die Wikipedia-REST-API nach.
- **Leere Karten** (z. B. B-52H, DC-3/C-47): Ursache war ein falscher Wikipedia-Titel (Kartenname ≠ Artikelname). → über eine **Titel-Zuordnungstabelle** korrigiert.
- **Falsche Bilder** (z. B. BAe 146 zeigte ein Logo): **Logo-/Wappen-Filter** blendet unpassende Treffer aus.

### 3c. Vollständigere Flughafen-Infrastruktur (Beispiel EDDF Terminal 2)
- Terminals werden **live aus OpenStreetMap** (Overpass API) geladen. Terminal 2 fehlte, weil es in OSM nur als `building=terminal` (statt `aeroway=terminal`) getaggt ist.
- **Fix:** Abfrage um `building=terminal` erweitert + Namensableitung aus dem `ref`-Tag → fehlende Terminals erscheinen jetzt.

---

## 4. Sicherheit & Architektur (Kernthema der Präsentation)

**Ausgangslage:** Der OpenAIP-API-Schlüssel (für die Luftraumkarten) war im öffentlichen Seiten-Code sichtbar.

**Bewertung des Risikos:** Read-only Kartendaten, kostenlos → kein Account-Zugriff, keine Kosten, kein echtes „Hacking"-Risiko; höchstens Kontingent-Mitnutzung. Dennoch ist ein exponierter Schlüssel unsaubere Praxis.

**Lösung — serverseitiger Proxy (Cloudflare Worker) als saubere Architektur:**
- Der Schlüssel kann als **verschlüsselte Umgebungsvariable im Worker** liegen, nie im Seiten-Code (Code liegt fertig als `worker_complete.js` bereit).
- Die Seiten rufen dann den Worker (`/oaip/tiles`, `/oaip/airspaces`) statt OpenAIP direkt.
- **Ergebnis:** Karten funktionieren für alle Besucher ohne eigenen Key, und der Schlüssel ist nirgends öffentlich sichtbar.

**Aktueller Betriebsmodus:** Für den sofortigen, aufwandsfreien Betrieb (ohne Deploy) wird derzeit ein geteilter, kostenloser Read-only-Kartenschlüssel direkt genutzt; ein eigener Key kann optional lokal (Browser) als Override hinterlegt werden. Der Worker-Proxy ist als **umschaltbare, sicherere Variante** vorbereitet. → Zeigt bewusst die **Abwägung Sicherheit ↔ Einfachheit**.

**Architektur-Prinzip:** Trennung von Geheimnis (Server) und Darstellung (Client) — dasselbe Muster, das bereits der KI-Assistent (Groq-Schlüssel im Worker) nutzt.

> Merksatz für die Folie: *„Der einzige Ort für einen API-Schlüssel ist der Server — nie der Browser."*

---

## 5. UI/UX & moderne Animationen

### 5a. Einheitliche Navigation
Identische dunkle Themen-Leiste (Start · Flughäfen · Flugzeuge · Drohnen · Lufträume) auf **allen** Seiten → konsistente Orientierung.

### 5b. Überarbeitete Einzelseiten
- **Drohnen-Seite:** Barrierefreiheits-Fehler behoben (unsichtbares Label), Kennzahlen & Filter-Zähler **datengetrieben** (bleiben automatisch korrekt), sichtbarer Tastatur-Fokus.
- **Lufträume-Seite:** modernisiertes Design (einheitliche Schrift, weiche Schatten, Pill-Filter), **einklappbare Legende**, mobile Optimierung.

### 5c. Moderne, scroll-gekoppelte Animationen („Apple-Stil")
- **Native CSS Scroll-Driven Animations** (`animation-timeline: view()`) — neuestes Browser-Feature (2024): Karten blenden **synchron zur Scroll-Position** ein (GPU-beschleunigt, ohne JavaScript-Ruckeln).
- **Hero-Parallax** (Drohnen-Seite): Kopfbereich gleitet beim Runterscrollen sanft weg.
- **Gestaffelte Einblendung** der Themenkarten auf der Startseite.
- **Progressive Enhancement / Fallback:** Browser ohne Scroll-Timeline-Support (Safari, Firefox) erhalten automatisch einen `IntersectionObserver`-Reveal — gleiche Wirkung.
- **Barrierefreiheit:** `prefers-reduced-motion` wird respektiert; ein sicheres Muster stellt sicher, dass **nie eine Karte unsichtbar hängen bleibt**.

---

## 6. Technische Highlights (für Nachfragen)

- **Serverlose Architektur:** statische GitHub-Pages-Seite + Cloudflare Worker als schlanker Secret-Proxy — kein eigener Server, kein Backend, keine Datenbank.
- **Ausschließlich CORS-freie, öffentliche APIs** im Browser: airplanes.live (ADS-B), Wikipedia/Wikidata (Daten & Bilder), OpenStreetMap/Overpass (Infrastruktur), OpenAIP (Lufträume, via Proxy).
- **Robustheit:** Fallback-Ketten überall (Bild-Fallback, API-Fallback, Animations-Fallback) → die Seite bleibt bei Einzelausfällen benutzbar.
- **Sicherheit:** Eingaben/Fremddaten werden sanitisiert & escaped; Secrets serverseitig.
- **Barrierefreiheit & Performance:** Reduced-Motion, Tastatur-Fokus, Canvas-Rendering für Massendaten, Lazy-Loading von Bildern.

---

## 7. Commit-Übersicht (chronologisch, Juni 2026)

1. Flugzeug-Deeplinks fokussieren + Kennnummer klickbar; Drohnen-/Lufträume-UI
2. Einheitliche dunkle Themen-Navigation (avx-topnav) auf allen Seiten
3. ADS-B: Flugzeugtyp weltweit live auf Weltkarte (airplanes.live) + Security-Hardening
4. Infrastruktur: Terminals auch via `building=terminal` + Ref-Namen (EDDF T2)
5. Katalog: Erstflug, Hersteller & Zulassung als Datenzeilen
6. Katalog: mehr Flugzeugdaten — kuratierte Kernwerte + Wikidata-Anreicherung
7. Security: geteilten OpenAIP-Key entfernt
8. Katalog: fehlende EXT-Flugzeugbilder via Wikipedia-Fallback
9. OpenAIP via Cloudflare-Worker-Proxy: Karten ohne Besucher-Key, Key geheim
10. Katalog: leere/falsche Flugzeugbilder beheben (Wiki-Titel + Logo-Filter)
11. Kompletter Cloudflare-Worker (Groq + OpenAIP-Proxy)
12. Drohnen: animate.css-Einblendungen (Karten + Modals)
13. Drohnen: Scroll-Reveal via IntersectionObserver
14. Katalog: Scroll-Reveal für Flugzeugkarten
15. Lufträume: dezente Einblend-Animationen für Panels/Overlays
16. Moderne Scroll-Driven-Animationen (`animation-timeline: view`) + IO-Fallback
17. Apple-Stil Scroll-/Reveal-Animationen auf alle Seiten ausgeweitet

---

## 8. Ausblick / offener Punkt

- **Cloudflare-Worker deployen:** Der fertige Worker-Code (`worker_complete.js`) muss einmalig im Cloudflare-Dashboard eingespielt und die Umgebungsvariable `OPENAIP_KEY` gesetzt werden. Danach laufen die Luftraumkarten für alle Besucher ohne sichtbaren Schlüssel.
- **Mögliche Erweiterungen:** Hero-Parallax auf weitere Seiten, tiefere Wikidata-Felder, weitere Länder-Terminals.
