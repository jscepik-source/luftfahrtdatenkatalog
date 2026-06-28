// ============================================================================
//  OpenAIP-Proxy für den Cloudflare-Worker (deploy.jscepik.workers.dev)
//  Zweck: Der OpenAIP-Key liegt NUR hier als geheime Env-Variable (OPENAIP_KEY)
//         und ist nie im öffentlichen Seiten-Code sichtbar. Die Karten rufen
//         den Worker statt OpenAIP direkt -> funktioniert für ALLE Besucher
//         ohne eigenen Key.
//
//  EINRICHTUNG (einmalig):
//   1) Cloudflare Dashboard -> Workers & Pages -> deinen Worker "deploy" öffnen
//      -> Settings -> Variables -> "Add variable"
//        Name:  OPENAIP_KEY
//        Value: 2800111e267cd352c035b2df2102fbdf   (dein bestehender Key)
//        -> "Encrypt" anklicken (macht ihn geheim) -> Save & Deploy
//   2) Die unten markierten Zeilen OBEN in deinen bestehenden fetch-Handler
//      einfügen (vor der Groq-Logik). Der Rest deines Workers bleibt unverändert.
//
//  Falls dein Worker ein "module worker" ist (export default { async fetch(request, env, ctx) }):
//  -> füge den Block am Anfang von fetch() ein, env ist bereits vorhanden.
// ============================================================================

// ----- HIER EINFÜGEN: ganz am Anfang von  async fetch(request, env, ctx) {  -----
//
//   const _u = new URL(request.url);
//   const _oaip = await handleOpenAip(_u, request, env);
//   if (_oaip) return _oaip;
//
// ----- ENDE EINFÜGEBLOCK -----


// ----- Diese Funktion irgendwo im Worker (außerhalb von fetch) ergänzen: -----
async function handleOpenAip(url, request, env) {
  const CORS = {
    'access-control-allow-origin': '*',
    'access-control-allow-headers': '*',
    'access-control-allow-methods': 'GET,OPTIONS',
  };
  // CORS-Preflight
  if (url.pathname.startsWith('/oaip/') && request.method === 'OPTIONS') {
    return new Response(null, { headers: CORS });
  }

  // 1) Luftraum-Kacheln:  /oaip/tiles/{z}/{x}/{y}.png
  if (url.pathname.startsWith('/oaip/tiles/')) {
    const rest = url.pathname.slice('/oaip/tiles/'.length); // z.B. 7/65/42.png
    const target = `https://api.tiles.openaip.net/api/data/openaip/${rest}?apiKey=${env.OPENAIP_KEY}`;
    const r = await fetch(target, { cf: { cacheTtl: 86400 } });
    return new Response(r.body, {
      status: r.status,
      headers: {
        ...CORS,
        'content-type': r.headers.get('content-type') || 'image/png',
        'cache-control': 'public, max-age=86400',
      },
    });
  }

  // 2) Luftraum-Polygone (JSON):  /oaip/airspaces?...
  if (url.pathname.startsWith('/oaip/airspaces')) {
    const target = `https://api.core.openaip.net/api/airspaces${url.search}`;
    const r = await fetch(target, { headers: { 'x-openaip-api-key': env.OPENAIP_KEY } });
    const body = await r.text();
    return new Response(body, {
      status: r.status,
      headers: { ...CORS, 'content-type': 'application/json; charset=utf-8' },
    });
  }

  return null; // kein OpenAIP-Pfad -> normale Worker-Logik (Groq) weiterlaufen lassen
}
