/* ============================================================================
 * zeitstempel.js — "Zuletzt aktualisiert"-Werte für den Luftfahrtdatenkatalog
 * ----------------------------------------------------------------------------
 * Umsetzung des Integrationsleitfadens: EIN Adapter pro Quellen-Kategorie
 * (Router-Muster). Jede Quelle hat in der Config ein Feld "kategorie"
 * (eine von sechs). Der Router lastUpdated(quelle) ruft den passenden Adapter
 * und liefert genau EINEN Zeitstempel als ISO-String — oder null — zurück.
 *
 *   "AIRAC"             -> currentAirac()    aktuelles AIRAC-Datum   (~103 Quellen)
 *   "API-Feld"          -> apiFeldAdapter()  Feld aus der API-Antwort (~52)
 *   "API/Dump"          -> dumpAdapter()     Datei-/Header-Zeitstempel (~17)
 *   "HTML"              -> htmlAdapter()     <meta>/Footer scrapen     (~22)
 *   "Publikationsdatum" -> manualLookup()    gepflegter Wert (Config)  (~33)
 *   "Nicht verfügbar"   -> () => null        keine Anzeige             (~2)
 *
 * Verwendung:
 *   const iso = await Zeitstempel.lastUpdated(quelle);
 *   el.textContent = Zeitstempel.formatStand(iso);   // "Stand: 11.06.2026, 14:23 UTC"
 *
 * Faustregel: Zeitstempel IMMER in UTC speichern/anzeigen.
 * ========================================================================== */
(function (global) {
  'use strict';

  // ── Hilfsfunktionen ────────────────────────────────────────────────────────

  // Deutsches Datum "DD.MM.YYYY" bzw. "DD.MM.YYYY HH:MM[:SS] [UTC]" als UTC parsen.
  // Wichtig: new Date("06.05.2026") liest das als MM.DD (5. Juni) — also falsch.
  const RE_DE = /^(\d{1,2})\.(\d{1,2})\.(\d{4})(?:[ T](\d{1,2}):(\d{2})(?::(\d{2}))?)?\s*(?:UTC|Z)?$/;
  function parseGerman(s) {
    const m = String(s).trim().match(RE_DE);
    if (!m) return null;
    const [, d, mo, y, hh, mi, ss] = m;
    return new Date(Date.UTC(+y, +mo - 1, +d, +(hh || 0), +(mi || 0), +(ss || 0)));
  }

  /** Beliebigen Wert (Date | String | Zahl | Unix-Epoch) in ISO-UTC wandeln, sonst null. */
  function toISO(v) {
    if (v == null || v === '') return null;
    if (typeof v === 'string') {
      const de = parseGerman(v);                  // deutsches Format zuerst probieren
      if (de) return de.toISOString();
      if (/^\d{9,13}$/.test(v.trim())) v = Number(v.trim());  // reiner Epoch-String
    }
    if (typeof v === 'number' && isFinite(v)) {
      const ms = v < 1e12 ? v * 1000 : v;         // < 1e12 => Unix-Sekunden (z. B. obsTime)
      const d = new Date(ms);
      return isNaN(d.getTime()) ? null : d.toISOString();
    }
    const d = (v instanceof Date) ? v : new Date(v);
    return isNaN(d.getTime()) ? null : d.toISOString();
  }

  /**
   * ISO-Zeitstempel als "Stand"-Text formatieren — in UTC.
   *   formatStand("2026-06-11T14:23:00Z")               -> "Stand: 11.06.2026, 14:23 UTC"
   *   formatStand(iso, { nurDatum: true })               -> "Stand: 11.06.2026"
   *   formatStand(null, { fallback: "manuell geprüft" }) -> "Stand: manuell geprüft"
   */
  function formatStand(iso, opts) {
    opts = opts || {};
    if (!iso) return 'Stand: ' + (opts.fallback || 'manuell geprüft');
    const d = new Date(iso);
    if (isNaN(d.getTime())) return 'Stand: ' + (opts.fallback || 'unbekannt');
    const p = n => String(n).padStart(2, '0');
    const datum = `${p(d.getUTCDate())}.${p(d.getUTCMonth() + 1)}.${d.getUTCFullYear()}`;
    if (opts.nurDatum) return `Stand: ${datum}`;
    return `Stand: ${datum}, ${p(d.getUTCHours())}:${p(d.getUTCMinutes())} UTC`;
  }

  // ── Kategorie 1: AIRAC (zentraler Kalender, KEIN Pro-Quelle-Request) ────────
  // AIP-Daten folgen dem weltweiten AIRAC-Zyklus: alle 28 Tage ein neuer Stand,
  // global synchron. Ein Kalender deckt damit alle AIP-Quellen ab.
  // Anker = bekannter Zyklusstart (00:00 UTC). Quelle: Integrationsleitfaden §5.
  const AIRAC_ANKER = '2026-06-11T00:00:00Z';
  const AIRAC_SPAN  = 28 * 864e5;                 // 28 Tage in Millisekunden
  const AIRAC_LISTE = [                            // kommende Zyklusstarts (Referenz)
    '2026-06-11', '2026-07-09', '2026-08-06', '2026-09-03', '2026-10-01',
    '2026-10-29', '2026-11-26', '2026-12-24', '2027-01-21', '2027-02-18'
  ];

  /** Aktuell gültiges AIRAC-Datum als Date (UTC). */
  function currentAirac(now) {
    now = now || new Date();
    const ref = new Date(AIRAC_ANKER).getTime();
    const cycles = Math.floor((now.getTime() - ref) / AIRAC_SPAN);
    return new Date(ref + cycles * AIRAC_SPAN);
  }

  /** AIRAC-Zyklusnummer "YYNN" (NN = wievielter 28-Tage-Zyklus im Jahr). */
  function airacCycle(date) {
    const ref = new Date(AIRAC_ANKER).getTime();
    const Y = date.getUTCFullYear();
    const yearStart = Date.UTC(Y, 0, 1);
    const kFirst = Math.ceil((yearStart - ref) / AIRAC_SPAN); // 1. Zyklusstart >= 1. Jan
    const firstStart = ref + kFirst * AIRAC_SPAN;
    const nn = Math.round((date.getTime() - firstStart) / AIRAC_SPAN) + 1;
    return `${String(Y).slice(-2)}${String(nn).padStart(2, '0')}`;
  }

  /** Komfort-Objekt: aktuelles + nächstes AIRAC inkl. Zyklusnummern. */
  function airacInfo(now) {
    const cur  = currentAirac(now);
    const next = new Date(cur.getTime() + AIRAC_SPAN);
    return {
      iso:        cur.toISOString(),
      effective:  cur,
      next:       next,
      cycle:      airacCycle(cur),    // z. B. "2606"
      nextCycle:  airacCycle(next)    // z. B. "2607"
    };
  }

  // ── Kategorie 2: API-Feld (Wetter, NOTAM, Verkehr) ──────────────────────────
  // Die Quelle liefert den Zeitstempel in DERSELBEN Antwort wie die Daten.
  // Entweder ein bereits geladenes Objekt übergeben (quelle.data / 2. Argument)
  // -> kein Extra-Request, oder quelle.apiUrl wird hier geholt.
  async function apiFeldAdapter(quelle, data) {
    data = data || (quelle && quelle.data) || null;
    if (!data && quelle && quelle.apiUrl) {
      const res = await fetch(quelle.apiUrl);
      data = await res.json();
    }
    if (Array.isArray(data)) data = data[0] || {};
    data = data || {};
    const ts =
      data.obsTime         // METAR/TAF-Beobachtung
      ?? data.observationTime
      ?? data.issueTime    // TAF-Vorhersage
      ?? data.runTime      // Wettermodell (ECMWF, Meteoblue, …)
      ?? data.modelRun
      ?? data.effectiveStart // NOTAM
      ?? data.created ?? data.issued
      ?? data.lastContact  // Flugtracking
      ?? data.lastSeen ?? data.timestamp;
    return toISO(ts);
  }

  /** METAR-Rohtext -> Beobachtungszeit (ISO). Liest die DDHHMMZ-Gruppe. */
  function metarObsTime(raw, now) {
    if (!raw) return null;
    const m = String(raw).match(/\b(\d{2})(\d{2})(\d{2})Z\b/);
    if (!m) return null;
    now = now || new Date();
    const day = +m[1], hh = +m[2], mm = +m[3];
    let y = now.getUTCFullYear(), mon = now.getUTCMonth();
    // Monatsübergang: liegt der Tag in der Zukunft, stammt er aus dem Vormonat.
    if (day > now.getUTCDate() + 1) { mon -= 1; if (mon < 0) { mon = 11; y -= 1; } }
    const d = new Date(Date.UTC(y, mon, day, hh, mm));
    return isNaN(d.getTime()) ? null : d.toISOString();
  }

  // ── Kategorie 3: API/Dump (tägliche Exporte, Datenbanken) ───────────────────
  // Zeitstempel steckt im Dump-Feld (generated/releaseDate/…) oder im
  // HTTP-Header Last-Modified der Datei.
  async function dumpAdapter(quelle) {
    quelle = quelle || {};
    if (quelle.dump) {
      const ts = quelle.dump.generated ?? quelle.dump.releaseDate
              ?? quelle.dump.aktualisiert ?? quelle.dump.updated;
      if (ts) return toISO(ts);
    }
    if (quelle.fileUrl) {
      const head = await fetch(quelle.fileUrl, { method: 'HEAD' });
      return toISO(head.headers.get('Last-Modified'));
    }
    return null;
  }

  // ── Kategorie 4: HTML (Behörden-, Hersteller-, Wiki-Seiten) ─────────────────
  // (a) Redaktionsdatum aus <meta>/Footer scrapen, (b) Fallback Last-Modified.
  // ACHTUNG: Last-Modified ist bei CMS-Seiten oft unzuverlässig (Cache-Zeit).
  // Hinweis: clientseitiges fetch() scheitert oft an CORS -> dann null
  // (Router fängt den Fehler ab). Zuverlässig über einen Proxy/Server.
  function scrapeFooterDate(html) {
    const m = String(html).match(/(\d{4}-\d{2}-\d{2})|(\d{1,2}[.\/]\d{1,2}[.\/]\d{2,4})/);
    return m ? m[0] : null;
  }
  async function htmlAdapter(quelle) {
    if (!quelle || !quelle.url) return null;
    try {
      const html = await (await fetch(quelle.url)).text();
      const m = html.match(/<meta[^>]+(?:last-modified|date|article:modified_time)[^>]+content="([^"]+)"/i);
      const ts = (m && m[1]) || scrapeFooterDate(html);
      if (ts) return toISO(ts);
    } catch (e) { /* CORS/Netz -> Fallback */ }
    try {
      const head = await fetch(quelle.url, { method: 'HEAD' });
      return toISO(head.headers.get('Last-Modified'));
    } catch (e) { return null; }
  }

  // ── Kategorie 5: Publikationsdatum (Normen, Berichte, Statistik) ────────────
  // Kein Live-Wert: gepflegtes Datum aus der Config.
  function manualLookup(quelle) {
    return toISO(quelle && (quelle.publishedDate || quelle.reviewedDate));
  }

  // ── Router / Dispatcher ─────────────────────────────────────────────────────
  const adapters = {
    'AIRAC':             ()  => currentAirac().toISOString(),
    'API-Feld':          (q) => apiFeldAdapter(q),
    'API/Dump':          (q) => dumpAdapter(q),
    'HTML':              (q) => htmlAdapter(q),
    'Publikationsdatum': (q) => manualLookup(q),
    'Nicht verfügbar':   ()  => null
  };

  /**
   * Zentraler Einstiegspunkt. Wählt anhand quelle.kategorie den Adapter,
   * fängt Fehler ab (kaputte Quelle blockiert nie die Seite) und gibt einen
   * ISO-Zeitstempel oder null zurück.
   */
  async function lastUpdated(quelle) {
    const fn = adapters[quelle && quelle.kategorie];
    if (!fn) return null;                       // unbekannte Kategorie -> keine Anzeige
    try {
      return await fn(quelle);
    } catch (e) {
      if (global.console) console.warn('[Zeitstempel]', quelle && quelle.id, e);
      return null;                              // Fallback statt Crash
    }
  }

  // ── Export ──────────────────────────────────────────────────────────────────
  const API = {
    lastUpdated, formatStand, toISO,
    currentAirac, airacInfo, airacCycle, AIRAC_LISTE,
    apiFeldAdapter, metarObsTime, dumpAdapter, htmlAdapter, manualLookup,
    adapters
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = API; // Node/Tests
  global.Zeitstempel = API;                                                   // Browser

})(typeof globalThis !== 'undefined' ? globalThis : this);
