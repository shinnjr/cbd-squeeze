// POST /api/charge — processor-agnostic charge seam (funnel-spec §3).
// TEST/mock until CBD gateway + Google Pay merchant credentials are configured.
// Never store raw payment tokens. Never use Stripe.

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
    },
  });
}

function tierUnit(qty) {
  if (qty === 1) return 127;
  if (qty === 2) return 108.5;
  return 99;
}

function expectedAmount(qty, subscribe) {
  const q = Math.max(1, Math.min(10, Number(qty) || 1));
  if (subscribe) return 107 * q;
  return tierUnit(q) * q;
}

function orderId() {
  const d = new Date();
  const y = d.getUTCFullYear();
  const r = crypto.randomUUID().replace(/-/g, "").slice(0, 8).toUpperCase();
  return `ST-${y}-${r}`;
}

function amountsMatch(a, b) {
  return Math.abs(Number(a) - Number(b)) < 0.009;
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "POST, OPTIONS",
      "access-control-allow-headers": "content-type, idempotency-key",
    },
  });
}

export async function onRequestPost(context) {
  try {
    const raw = await context.request.text();
    if (!raw || raw.length > 8192) {
      return json(400, { status: "error", error: "bad_request" });
    }
    let body;
    try {
      body = JSON.parse(raw);
    } catch {
      return json(400, { status: "error", error: "invalid_json" });
    }

    const order = body.order || {};
    const payment = body.payment || {};
    const qty = Number(order.qty);
    const subscribe = !!order.subscribe;
    const amount = Number(order.amount);

    if (!Number.isFinite(qty) || qty < 1 || qty > 10) {
      return json(400, { status: "error", error: "bad_qty" });
    }
    if (!Number.isFinite(amount)) {
      return json(400, { status: "error", error: "bad_amount" });
    }
    const expected = expectedAmount(qty, subscribe);
    if (!amountsMatch(amount, expected)) {
      return json(400, {
        status: "error",
        error: "amount_mismatch",
        expected,
      });
    }
    if (order.sku && order.sku !== "ST-CONCENTRATE-10000") {
      return json(400, { status: "error", error: "bad_sku" });
    }

    const idem =
      context.request.headers.get("idempotency-key") ||
      body.idempotencyKey ||
      "";

    // Idempotent replay if we already stored this key
    const kv = context.env.ST_ORDERS || context.env.ST_LEADS || null;
    if (kv && idem) {
      try {
        const prev = await kv.get("idem:" + idem);
        if (prev) {
          const parsed = JSON.parse(prev);
          return json(200, {
            status: "success",
            orderId: parsed.orderId,
            amount: parsed.amount,
            email: parsed.email || null,
            mode: parsed.mode || "TEST",
            replayed: true,
          });
        }
      } catch {}
    }

    const mode = (context.env.PAYMENT_MODE || "TEST").toUpperCase();
    const hasLive =
      mode === "PRODUCTION" &&
      context.env.PAYMENT_GATEWAY &&
      context.env.PAYMENT_GATEWAY_SECRET;

    // Live processor plug-in point (not wired — needs James-chosen CBD PSP + secrets)
    if (hasLive) {
      return json(501, {
        status: "error",
        error: "processor_not_wired",
        message:
          "PRODUCTION mode set but gateway adapter not implemented for this deploy. Stay on TEST or wire the chosen CBD processor.",
      });
    }

    // TEST path: accept absence of real token (UI currently can't mint GPay without merchantId)
    // When token present, still do not forward to a real PSP here.
    const id = orderId();
    const email = typeof payment.email === "string" ? payment.email.slice(0, 200) : null;
    const record = {
      orderId: id,
      sku: "ST-CONCENTRATE-10000",
      qty,
      subscribe,
      amount: expected,
      email,
      gateway: body.gateway || null,
      mode: "TEST",
      ts: new Date().toISOString(),
      // intentionally omit payment.token
    };

    if (kv) {
      try {
        await kv.put("order:" + id, JSON.stringify(record));
        if (idem) await kv.put("idem:" + idem, JSON.stringify(record), { expirationTtl: 86400 });
        const day = "orders:" + new Date().toISOString().slice(0, 10);
        const prev = (await kv.get(day)) || "";
        await kv.put(
          day,
          prev +
            JSON.stringify({
              orderId: id,
              amount: expected,
              qty,
              subscribe,
              email: email ? email.replace(/(^.).*(@.*$)/, "$1***$2") : null,
              ts: record.ts,
              mode: "TEST",
            }) +
            "\n"
        );
      } catch {}
    }

    return json(200, {
      status: "success",
      orderId: id,
      amount: expected,
      email,
      mode: "TEST",
    });
  } catch {
    return json(500, { status: "error", error: "server_error" });
  }
}
