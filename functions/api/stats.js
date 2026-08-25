// /api/stats — event counts (no PII). Returns JSON tallies per event type.
export async function onRequestGet(context) {
  try {
    const data = await context.env.ST_TRACK.get("events"); // future: aggregate storage
    return new Response(JSON.stringify({ ok: true, note: "readback pending KV aggregation", raw: data ? data.length : 0 }), {
      headers: { "content-type": "application/json" }
    });
  } catch {
    return new Response(JSON.stringify({ ok: false }), { status: 200, headers: { "content-type": "application/json" } });
  }
}
