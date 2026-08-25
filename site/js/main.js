/* Simple Tinctures — main.js. Nav, savings calculator, email capture, order form, year. */
(function () {
  "use strict";

  /* footer year */
  var yr = document.querySelector("[data-year]");
  if (yr) yr.textContent = String(new Date().getFullYear());

  /* nav scroll shadow */
  var nav = document.querySelector("nav");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* mobile nav */
  var toggle = document.getElementById("navToggle");
  var links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "✕" : "☰";
    });
  }

  /* savings calculator */
  var bottlesEl = document.getElementById("bottles");
  var priceEl = document.getElementById("price");
  var storeEl = document.getElementById("calc-store");
  var gdEl = document.getElementById("calc-gd");
  var saveEl = document.getElementById("calc-save");

  function money(n) {
    return "$" + Math.round(n).toLocaleString("en-US");
  }

  function recalc() {
    if (!bottlesEl || !priceEl) return;
    var perMonth = Math.max(1, parseInt(bottlesEl.value, 10) || 1);
    var perBottle = Math.max(0, parseFloat(priceEl.value) || 0);
    var perYear = perMonth * 12;

    var storeYear = perYear * perBottle;
    var concentrateBottles = Math.ceil(perYear / 8);
    var gdYear = concentrateBottles * 127 + perYear * 1.25; /* $127/bottle + ~$1.25 MCT per tincture */
    var saved = Math.max(0, storeYear - gdYear);

    if (storeEl) storeEl.textContent = money(storeYear) + " / yr";
    if (gdEl) gdEl.textContent = money(gdYear) + " / yr";
    if (saveEl) saveEl.textContent = money(saved) + " saved / yr";
  }

  if (bottlesEl && priceEl) {
    bottlesEl.addEventListener("input", recalc);
    priceEl.addEventListener("input", recalc);
    recalc();
  }

  /* email capture (dosing guide + $10 code) → POST /api/subscribe */
  var cap = document.getElementById("captureForm");
  if (cap) {
    cap.addEventListener("submit", function (e) {
      e.preventDefault();
      var input = cap.querySelector("input[type=email]");
      if (!input || !input.value) return;
      var email = input.value.trim();
      var tokenEl = cap.querySelector('[name="cf-turnstile-response"]');
      var token = tokenEl ? tokenEl.value : "";
      if (!token) {
        cap.innerHTML = '<p style="margin:0;font-weight:600;color:#fff">Please wait a moment and try again.</p>';
        return;
      }
      try {
        fetch("/api/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email, source: "dosing-guide", "cf-turnstile-response": token })
        }).catch(function () {});
      } catch (err) {}
      cap.innerHTML =
        '<p style="margin:0;font-weight:600;color:#fff">You\'re in — check your inbox for the guide and your $10 code.</p>';
    });
  }

  /* scroll reveal */
  var rv = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && rv.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) { io.observe(el); });
  } else { rv.forEach(function (el) { el.classList.add("in"); }); }

})();
