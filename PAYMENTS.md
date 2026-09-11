# Payments — Simple Tinctures

## Customer rule
Google Pay only. Never Stripe / PayPal / Venmo / Zelle as the customer checkout story.

## Current state
- `site/js/checkout.js` — GPay UI; `PAYMENT.gateway` + `PAYMENT.googleMerchantId` are null → shows reserve fallback (honest).
- `POST /api/charge` — TEST/mock charge seam with amount re-validation + optional idempotency. No live PSP.
- `/order/confirmed` — confirmation page.

## Go-live checklist (James)
1. Pick a CBD-capable processor with Google Pay (+ Apple Pay preferred): e.g. candidates in funnel-spec (seer / ezeepay / cbdpay / bankcardusa / CardConnect / Worldpay / NMI / Elavon — verify current CBD policy).
2. Open Google Pay Business Console merchant ID tied to that processor.
3. Set in `checkout.js` (or better: inject from a tiny config endpoint):
   - `PAYMENT.gateway`
   - `PAYMENT.googleMerchantId`
   - `PAYMENT.environment = 'PRODUCTION'` only after bank + inventory/COA gate
4. Set Pages secrets: `PAYMENT_MODE=PRODUCTION`, `PAYMENT_GATEWAY=...`, `PAYMENT_GATEWAY_SECRET=...` and implement the adapter branch in `functions/api/charge.js`.
5. Optional KV binding `ST_ORDERS` (falls back to `ST_LEADS` today).
6. One TEST purchase, then one live $1/smoke, then full $127.

## Deploy
From repo root: `npx wrangler pages deploy site --project-name=simpletinctures` (needs valid Cloudflare API token).
