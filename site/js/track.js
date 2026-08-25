// Simple Tinctures — first-party analytics beacon (no paid tools, no cookies).
// POSTs minimal events to /api/track (Pages Function → appends NDJSON to KV/R2 or logs).
(function () {
  "use strict";
  var endpoint = "/api/track";
  function send(ev, data) {
    try {
      var payload = JSON.stringify({
        e: ev, d: data || {}, t: Date.now(),
        p: location.pathname, r: document.referrer || "",
        w: innerWidth, lang: navigator.language
      });
      if (navigator.sendBeacon) navigator.sendBeacon(endpoint, payload);
      else fetch(endpoint, { method: "POST", body: payload, keepalive: true }).catch(function(){});
    } catch (e) {}
  }
  window.stTrack = send;
  send("pageview");

  // funnel events (delegated so it works on any page)
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-st]");
    if (el) send(el.getAttribute("data-st"), { label: el.getAttribute("data-label") || "" });
  }, true);

  // band clicks on homepage brutal picker + calc
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest(".band");
    if (b && b.textContent) send("band_click", { label: b.textContent.trim().slice(0, 40) });
  }, true);

  // calculator slider engagement (once per session)
  var sliderUsed = false;
  document.addEventListener("input", function (ev) {
    if (ev.target && ev.target.id === "mg" && !sliderUsed) {
      sliderUsed = true; send("calc_used");
    }
  });
})();
