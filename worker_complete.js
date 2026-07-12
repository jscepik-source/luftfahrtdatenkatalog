// ============================================================================
//  KOMPLETTER Cloudflare-Worker für  deploy.DEIN-NAME.workers.dev
//  Ersetzt deinen bisherigen Worker-Code 1:1 und kann zusätzlich OpenAIP.
//
//  Aufgaben:
//   1) KI-Proxy (Groq)  – POST /        Body { payload: {model, messages, ...} }
//                                        -> Groq, Key = env.GROQ_KEY
//   2) OpenAIP-Kacheln  – GET /oaip/tiles/{z}/{x}/{y}.png
//   3) OpenAIP-Polygone – GET /oaip/airspaces?...   Key = env.OPENAIP_KEY
//
//  EINRICHTUNG (Cloudflare Dashboard -> Worker "deploy"):
//   A) Settings -> Variables -> zwei Variablen (jeweils "Encrypt"):
//        GROQ_KEY     = <dein Groq-Key>
//        OPENAIP_KEY  = <dein OpenAIP-Key>   (NIE einen echten Key hier im Klartext ablegen)
//   B) Den GESAMTEN Code unten in den Worker-Editor einfügen -> Save & Deploy.
//
//  HINWEIS: Falls dein bisheriger Worker noch ANDERE Dinge macht (außer der KI),
//  kopier ihn mir – dann führe ich beides zusammen, statt zu ersetzen.
// ============================================================================

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': '*',
  'access-control-allow-methods': 'GET,POST,OPTIONS',
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS-Preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    // ── 2) OpenAIP: Luftraum-Kacheln  /oaip/tiles/{z}/{x}/{y}.png ──
    if (url.pathname.startsWith('/oaip/tiles/')) {
      const rest = url.pathname.slice('/oaip/tiles/'.length); // z.B. 7/65/42.png
      const target = `https://api.tiles.openaip.net/api/data/openaip/${rest}?apiKey=${env.OPENAIP_KEY}`;
      const r = await fetch(target, { cf: { cacheTtl: 86400, cacheEverything: true } });
      return new Response(r.body, {
        status: r.status,
        headers: {
          ...CORS,
          'content-type': r.headers.get('content-type') || 'image/png',
          'cache-control': 'public, max-age=86400',
        },
      });
    }

    // ── 3) OpenAIP: Luftraum-Polygone (JSON)  /oaip/airspaces?... ──
    if (url.pathname.startsWith('/oaip/airspaces')) {
      const target = `https://api.core.openaip.net/api/airspaces${url.search}`;
      const r = await fetch(target, { headers: { 'x-openaip-api-key': env.OPENAIP_KEY } });
      const body = await r.text();
      return new Response(body, {
        status: r.status,
        headers: { ...CORS, 'content-type': 'application/json; charset=utf-8' },
      });
    }

    // ── 1) KI-Proxy (Groq):  POST /  mit { payload: {...} } ──
    if (request.method === 'POST') {
      try {
        const inb = await request.json();
        const payload = inb && inb.payload ? inb.payload : inb; // toleriert beide Formen
        const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${env.GROQ_KEY}`,
          },
          body: JSON.stringify(payload),
        });
        const body = await r.text();
        return new Response(body, {
          status: r.status,
          headers: { ...CORS, 'content-type': 'application/json; charset=utf-8' },
        });
      } catch (e) {
        return new Response(JSON.stringify({ error: String(e && e.message || e) }), {
          status: 500,
          headers: { ...CORS, 'content-type': 'application/json' },
        });
      }
    }

    // Health-Check (GET /)
    return new Response('OK – Worker laeuft (Groq + OpenAIP-Proxy)', {
      headers: { ...CORS, 'content-type': 'text/plain; charset=utf-8' },
    });
  },
};
