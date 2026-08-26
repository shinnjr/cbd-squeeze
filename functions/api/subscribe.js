// /api/subscribe — email capture sink → ST_LEADS KV (NDJSON per day)
export async function onRequestPost(context) {
  try {
    const body = await context.request.text();
    if (!body || body.length > 300) return new Response("ok");
    let ev; try { ev = JSON.parse(body); } catch { return new Response("ok"); }
    if (!ev.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(ev.email)) return new Response("ok");
    const line = JSON.stringify({ email: ev.email, source: ev.source || "", ts: new Date().toISOString() }) + "\n";
    const k = "leads:" + new Date().toISOString().slice(0, 10);
    try {
      const prev = (await context.env.ST_LEADS.get(k)) || "";
      await context.env.ST_LEADS.put(k, prev + line);
    } catch {}
    return new Response("ok", { headers: { "content-type": "text/plain" } });
  } catch { return new Response("ok"); }
}
