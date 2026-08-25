// /api/track — first-party event sink. Appends NDJSON lines; queryable via wrangler tail or D1 later.
export async function onRequestPost(context) {
  try {
    const body = await context.request.text();
    // basic size guard
    if (!body || body.length > 512) return new Response("ok");
    let ev;
    try { ev = JSON.parse(body); } catch { return new Response("ok"); }
    const line = JSON.stringify({ ...ev, ip: undefined, ua: context.request.headers.get("user-agent") || "" }) + "\n";
    // Store in the Pages KV binding if present (ST_TRACK), else no-op success.
    try {
      await context.env.ST_TRACK.append(line);
    } catch {}
    return new Response("ok", { headers: { "content-type": "text/plain" } });
  } catch {
    return new Response("ok");
  }
}
