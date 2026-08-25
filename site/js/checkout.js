/* Simple Tinctures — checkout.js. Qty stepper, tiered pricing, subscribe, Google Pay (PaymentRequest), reserve fallback.
   Charge path: POST /api/charge (processor-agnostic contract) -> navigate /order/confirmed. */
(function () {
  "use strict";

  /* ---- PROCESSOR CONFIG (swappable backend) ---- */
  var PAYMENT = {
    gateway: null,            // set when CBD processor live: 'cardconnect' | 'worldpay' | ... (see funnel-spec §3.1)
    googleMerchantId: null,   // from Google Pay business console (tied to processor)
    environment: 'TEST',      // 'TEST' -> 'PRODUCTION' at go-live
    chargeEndpoint: '/api/charge'
  };

  var qty = 1, subscribed = false;

  /* ---- ?plan= deep-link (v2 homepage funnels: single|double|sub) ---- */
  try {
    var plan = new URLSearchParams(location.search).get("plan");
    if (plan === "double") { qty = 2; }
    if (plan === "sub")    { subscribed = true; }
  } catch (e) {}


  function tierUnit(q) { return q === 1 ? 127 : q === 2 ? 108.5 : 99; } // $127 / $217 double / multi-bottle
  function total() {
    if (subscribed) return 107 * qty; // $107/mo subscription per bottle
    return tierUnit(qty) * qty;
  }
  function money(n) { return "$" + n.toFixed(2).replace(/\.00$/, ""); }

  var qVal = document.getElementById("qtyVal");
  var qMinus = document.getElementById("qMinus");
  var qPlus = document.getElementById("qPlus");
  var tierLine = document.getElementById("tierLine");
  var subToggle = document.getElementById("subscribe");
  var gpayTotal = document.getElementById("gpayTotal");
  var gpayBtn = document.getElementById("gpayBtn");
  var reserveBox = document.getElementById("reserveBox");
  var statusMsg = document.getElementById("statusMsg");

  function render() {
    var t = total();
    if (qVal) qVal.textContent = String(qty);
    if (tierLine) {
      var label = subscribed ? "$107/mo — " + qty + (qty === 1 ? " bottle" : " bottles") + "/mo" : qty === 1 ? "1 bottle — $127" : qty + " bottles — " + money(tierUnit(qty) * qty);
      tierLine.textContent = label;
    }
    if (gpayTotal) gpayTotal.textContent = money(t);
    if (gpayBtn) gpayBtn.innerHTML = 'Buy with Google Pay — <span id="gpayTotal">' + money(t) + "</span>";
  }

  if (qMinus) qMinus.addEventListener("click", function () { qty = Math.max(1, qty - 1); render(); });
  if (qPlus) qPlus.addEventListener("click", function () { qty = Math.min(10, qty + 1); render(); });
  if (subToggle) subToggle.addEventListener("change", function () { subscribed = subToggle.checked; render(); });

  function setStatus(text, isError) {
    if (!statusMsg) return;
    statusMsg.textContent = text;
    statusMsg.hidden = false;
    statusMsg.className = "status-msg" + (isError ? " error" : "");
  }
  function clearStatus() { if (statusMsg) { statusMsg.hidden = true; statusMsg.textContent = ""; } }

  function gpayToken(details) {
    // Standard PaymentRequest GPay token shape. Guard against processor-specific variants.
    try {
      return details.paymentMethodData && details.paymentMethodData.tokenizationData
        ? details.paymentMethodData.tokenizationData.token
        : (details.token || null);
    } catch (e) { return details && details.token ? details.token : null; }
  }

  function confirmUrl(data, result) {
    var q = "order=" + encodeURIComponent(data.orderId) +
            "&amount=" + total().toFixed(2) +
            "&qty=" + qty +
            "&subscribe=" + (subscribed ? "1" : "0");
    if (result.payerEmail) q += "&email=" + encodeURIComponent(result.payerEmail);
    if (result.payerName) q += "&name=" + encodeURIComponent(result.payerName);
    return "/order/confirmed?" + q;
  }

  /* ---- Google Pay (PaymentRequest) with honest fallback until processor is live ---- */
  if (gpayBtn) {
    gpayBtn.addEventListener("click", function () {
      clearStatus();
      if (!PAYMENT.googleMerchantId || !PAYMENT.gateway) {
        if (reserveBox) { reserveBox.hidden = false; reserveBox.scrollIntoView({ behavior: "smooth", block: "center" }); }
        return;
      }
      var t = total();
      var methodData = [{
        supportedMethods: "https://google.com/pay",
        data: {
          environment: PAYMENT.environment,
          apiVersion: 2,
          apiVersionMinor: 0,
          merchantInfo: { merchantId: PAYMENT.googleMerchantId, merchantName: "Simple Tinctures" },
          allowedPaymentMethods: [{
            type: "CARD",
            parameters: { allowedAuthMethods: ["PAN_ONLY", "CRYPTOGRAM_3DS"], allowedCardNetworks: ["VISA", "MASTERCARD", "AMEX"] },
            tokenizationSpecification: { type: "PAYMENT_GATEWAY", parameters: { gateway: "simple-tinctures-gateway", gatewayMerchantId: "simple-tinctures" } }
          }]
        }
      }];
      var details = {
        total: { label: "Simple Tinctures", amount: { currency: "USD", value: t.toFixed(2) } },
        displayItems: [{ label: "Concentrate × " + qty + (subscribed ? " (subscribe)" : ""), amount: { currency: "USD", value: t.toFixed(2) } }]
      };
      var request;
      try { request = new PaymentRequest(methodData, details); }
      catch (e) { if (reserveBox) reserveBox.hidden = false; return; }

      request.show().then(function (result) {
        setStatus("Processing…", false);
        var payload = {
          gateway: PAYMENT.gateway,
          order: { sku: "ST-CONCENTRATE-10000", qty: qty, subscribe: subscribed, amount: t },
          payment: {
            token: gpayToken(result.details),
            email: result.payerEmail || null,
            name: result.payerName || null,
            shipping: result.shippingAddress || null,
            phone: result.payerPhone || null
          }
        };
        fetch(PAYMENT.chargeEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }).then(function (r) { return r.json(); }).then(function (data) {
          if (data && data.status === "success" && data.orderId) {
            result.complete("success");
            window.location.href = confirmUrl(data, result);
          } else {
            result.complete("fail");
            setStatus("Payment didn't go through. Tap to try again or use a different card.", true);
          }
        }).catch(function () {
          result.complete("fail");
          setStatus("We couldn't complete payment. Your card was not charged. Please try again.", true);
        });
      }).catch(function () { clearStatus(); /* user cancelled or declined — no-op */ });
    });
  }

  /* ---- reserve fallback (email capture) ---- */
  var reserveForm = document.getElementById("reserveForm");
  if (reserveForm) {
    reserveForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = reserveForm.querySelector("input[type=email]");
      if (!input || !input.value) return;
      var email = input.value.trim();
      try {
        fetch("/api/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email, source: "reserve" })
        }).catch(function () {});
      } catch (err) {}
      reserveForm.innerHTML = '<p style="margin:0;font-weight:600;color:var(--green)">You\'re on the list — we\'ll email you the moment checkout is live, plus your $10 code.</p>';
    });
  }

  /* sync UI with deep-linked state */
  try {
    var sub = document.getElementById("subscribe");
    if (sub) sub.checked = subscribed;
    var pl = new URLSearchParams(location.search).get("plan");
    if (pl === "double" && qMinus) { /* qty already 2; nothing visual beyond stepper */ }
  } catch (e) {}
  render();
})();
