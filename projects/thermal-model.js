/* Interactive version of SingleCellLumped.m.
   Same two-state model (cell temperature + state of charge), same inputs, solved in the browser
   so a visitor can change the assumptions and watch the temperature curve respond. */
(function () {
  "use strict";
  var D = window.THERMAL_DATA;
  var root = document.getElementById("thermal-sim");
  if (!D || !root) return;

  // ---- fixed model constants (match the MATLAB script) ----
  var LAPS = 20, N_SERIES = 140, MASS = 0.069, Q_CELL = 4.6 * 3600; // kg, coulombs
  var LIMIT_C = 60;     // Formula SAE maximum cell temperature
  var STEP = 0.04;      // integration step (s)
  var RUN_S = LAPS * D.lapDuration;

  var CONTROLS = [
    { key: "hA", label: "Cooling (hA)", unit: "W/K", min: 0, max: 2, step: 0.05, def: 0.2, digits: 2,
      hint: "Heat the cell can shed to the air per degree above ambient." },
    { key: "tAmb", label: "Ambient temperature", unit: "°C", min: 10, max: 45, step: 1, def: 25, digits: 0 },
    { key: "t0", label: "Starting cell temperature", unit: "°C", min: 15, max: 45, step: 1, def: 30, digits: 0 },
    { key: "parallel", label: "Cells in parallel", unit: "P", min: 2, max: 6, step: 1, def: 3, digits: 0,
      hint: "More parallel cells share the same pack power, so each carries less current." },
    { key: "cp", label: "Specific heat (cp)", unit: "J/kg·K", min: 700, max: 1200, step: 10, def: 900, digits: 0 }
  ];
  var DEFAULTS = {};
  CONTROLS.forEach(function (c) { DEFAULTS[c.key] = c.def; });

  // ---- model ----
  // Linear lookup on an evenly spaced table, extrapolating past the ends like interp1(...,'extrap').
  function lut(arr, start, step, x) {
    var f = (x - start) / step, i = Math.floor(f);
    if (i < 0) i = 0;
    if (i > arr.length - 2) i = arr.length - 2;
    return arr[i] + (f - i) * (arr[i + 1] - arr[i]);
  }
  function packPowerW(t) {
    var p = D.lapPowerKW, f = (t % D.lapDuration) / D.powerDt, i = Math.floor(f);
    if (i > p.length - 2) i = p.length - 2;
    return (p[i] + (f - i) * (p[i + 1] - p[i])) * 1000;
  }
  function simulate(prm) {
    var nCells = N_SERIES * prm.parallel, mcp = MASS * prm.cp;
    var T = prm.t0, soc = 1, peakT = T, peakI = 0, depletedAt = null;
    var out = { t: [0], T: [T], soc: [soc] };
    var cur = 0; // current from the most recent derivative evaluation
    function deriv(t, T, soc) {
      var R = lut(D.dcirMilliOhm, D.dcirSocStart, D.dcirSocStep, soc * 100) / 1000;
      var P = packPowerW(t) / nCells;
      var voc = lut(D.vocVolts, D.vocSocStart, D.vocSocStep, soc * 100);
      var disc = voc * voc - 4 * P * R;            // terminal voltage under load (voltage sag)
      var v = (voc + Math.sqrt(disc > 0 ? disc : 0)) / 2;
      cur = P / v;
      return [(cur * cur * R - prm.hA * (T - prm.tAmb)) / mcp, -cur / Q_CELL];
    }
    var steps = Math.round(RUN_S / STEP), perSample = Math.round(1 / STEP);
    for (var n = 0; n < steps; n++) {
      var t = n * STEP;
      var k1 = deriv(t, T, soc);
      if (cur > peakI) peakI = cur;
      var k2 = deriv(t + STEP, T + STEP * k1[0], soc + STEP * k1[1]);   // Heun's method
      T += STEP * 0.5 * (k1[0] + k2[0]);
      soc += STEP * 0.5 * (k1[1] + k2[1]);
      if (T > peakT) peakT = T;
      if (soc <= 0) { soc = 0; depletedAt = (t + STEP) / 60; }
      if ((n + 1) % perSample === 0 || depletedAt !== null || n === steps - 1) {
        out.t.push((t + STEP) / 60); out.T.push(T); out.soc.push(soc);
      }
      if (depletedAt !== null) break;
    }
    out.peakT = peakT; out.peakI = peakI; out.depletedAt = depletedAt;
    out.finalT = T; out.finalSoc = soc;
    return out;
  }
  window.thermalSimulate = simulate; // exposed for testing

  // ---- page structure ----
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  var state = {};
  var inputs = {}, outputs = {};
  var controlsBox = el("div", "sim-controls");
  CONTROLS.forEach(function (c) {
    state[c.key] = c.def;
    var row = el("label", "sim-control");
    var head = el("span", "sim-control-head");
    head.appendChild(el("span", "sim-control-name", c.label));
    var val = el("output", "sim-control-val");
    head.appendChild(val);
    row.appendChild(head);
    var inp = el("input");
    inp.type = "range"; inp.min = c.min; inp.max = c.max; inp.step = c.step; inp.value = c.def;
    if (c.hint) inp.title = c.hint;
    inp.addEventListener("input", function () { state[c.key] = parseFloat(inp.value); update(); });
    row.appendChild(inp);
    inputs[c.key] = inp; outputs[c.key] = val;
    controlsBox.appendChild(row);
  });
  var reset = el("button", "sim-reset", "Reset to defaults");
  reset.type = "button";
  reset.addEventListener("click", function () {
    CONTROLS.forEach(function (c) { state[c.key] = c.def; inputs[c.key].value = c.def; });
    update();
  });
  controlsBox.appendChild(reset);

  var main = el("div", "sim-main");
  var stats = el("dl", "sim-stats");
  var legend = el("div", "sim-legend",
    '<span><i class="sim-key sim-key-live"></i>Your settings</span>' +
    '<span><i class="sim-key sim-key-base"></i>Default settings</span>');
  var plot = el("div", "sim-plot");
  var tip = el("div", "sim-tip");
  tip.hidden = true;
  var note = el("p", "sim-note");
  main.appendChild(stats); main.appendChild(legend); main.appendChild(plot); main.appendChild(note);

  root.textContent = "";
  root.appendChild(controlsBox);
  root.appendChild(main);

  var baseline = simulate(DEFAULTS);
  var live = baseline;
  var geom = null;

  // ---- chart ----
  function niceStep(span) {
    var steps = [1, 2, 5, 10, 20, 50];
    for (var i = 0; i < steps.length; i++) if (span / steps[i] <= 7) return steps[i];
    return 100;
  }
  function pathFor(run, x, y) {
    var d = "";
    for (var i = 0; i < run.t.length; i++) d += (i ? "L" : "M") + x(run.t[i]).toFixed(1) + " " + y(run.T[i]).toFixed(1);
    return d;
  }
  function draw() {
    var W = Math.max(280, Math.round(plot.clientWidth));
    var H = Math.round(Math.min(400, Math.max(250, W * 0.52)));
    var m = { l: 46, r: 14, t: 12, b: 38 };
    var xMax = RUN_S / 60;
    var lo = Math.min(Math.min.apply(null, live.T), Math.min.apply(null, baseline.T));
    var hi = Math.max(live.peakT, baseline.peakT);
    var step = niceStep(hi - lo + 2);
    var y0 = Math.floor((lo - 0.5) / step) * step, y1 = Math.ceil((hi + 0.5) / step) * step;
    var showLimit = y1 >= LIMIT_C - step;
    if (showLimit && y1 < LIMIT_C + step) y1 = Math.ceil((LIMIT_C + 1) / step) * step;
    var x = function (v) { return m.l + (v / xMax) * (W - m.l - m.r); };
    var y = function (v) { return H - m.b - ((v - y0) / (y1 - y0)) * (H - m.t - m.b); };
    var s = '<svg width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + " " + H +
      '" role="img" aria-label="Cell temperature over the endurance run for the chosen settings">';
    for (var v = y0; v <= y1 + 1e-9; v += step) {
      s += '<line class="sim-grid" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y(v) + '" y2="' + y(v) + '"/>' +
        '<text class="sim-tick" x="' + (m.l - 8) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + v + "</text>";
    }
    for (var tx = 0; tx <= xMax; tx += 5) {
      s += '<text class="sim-tick" x="' + x(tx) + '" y="' + (H - m.b + 18) + '" text-anchor="middle">' + tx + "</text>";
    }
    s += '<line class="sim-axis" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + (H - m.b) + '" y2="' + (H - m.b) + '"/>' +
      '<text class="sim-label" x="' + (m.l + (W - m.l - m.r) / 2) + '" y="' + (H - 4) + '" text-anchor="middle">Time (min)</text>';
    if (showLimit) {
      s += '<line class="sim-limit" x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y(LIMIT_C) + '" y2="' + y(LIMIT_C) + '"/>' +
        '<text class="sim-limit-label" x="' + (W - m.r - 4) + '" y="' + (y(LIMIT_C) - 6) + '" text-anchor="end">60 °C rules limit</text>';
    }
    s += '<path class="sim-line-base" d="' + pathFor(baseline, x, y) + '"/>' +
      '<path class="sim-line-live" d="' + pathFor(live, x, y) + '"/>' +
      '<g class="sim-hover" visibility="hidden"><line class="sim-cross" y1="' + m.t + '" y2="' + (H - m.b) + '"/>' +
      '<circle class="sim-dot-base" r="4"/><circle class="sim-dot-live" r="5"/></g>' +
      '<rect class="sim-hit" x="' + m.l + '" y="' + m.t + '" width="' + (W - m.l - m.r) + '" height="' + (H - m.t - m.b) + '"/>' +
      "</svg>";
    plot.innerHTML = s;
    tip.hidden = true;
    plot.appendChild(tip);
    geom = { x: x, y: y, m: m, W: W, H: H, xMax: xMax };
    var hit = plot.querySelector(".sim-hit");
    hit.addEventListener("pointermove", onMove);
    hit.addEventListener("pointerdown", onMove);
    hit.addEventListener("pointerleave", hideHover);
  }
  function sampleAt(run, tMin) {
    // samples are one per second, so the index is the time in seconds
    var i = Math.round(tMin * 60);
    if (i > run.t.length - 1) return null;
    return { t: run.t[i], T: run.T[i], soc: run.soc[i] };
  }
  function onMove(ev) {
    if (!geom) return;
    var box = plot.querySelector("svg").getBoundingClientRect();
    var px = ev.clientX - box.left;
    var tMin = Math.max(0, Math.min(geom.xMax, ((px - geom.m.l) / (geom.W - geom.m.l - geom.m.r)) * geom.xMax));
    var a = sampleAt(live, tMin), b = sampleAt(baseline, tMin);
    if (!a) a = { t: live.t[live.t.length - 1], T: live.finalT, soc: live.finalSoc };
    var g = plot.querySelector(".sim-hover");
    var cx = geom.x(a.t);
    g.setAttribute("visibility", "visible");
    var cross = g.querySelector(".sim-cross");
    cross.setAttribute("x1", cx); cross.setAttribute("x2", cx);
    var dl = g.querySelector(".sim-dot-live");
    dl.setAttribute("cx", cx); dl.setAttribute("cy", geom.y(a.T));
    var db = g.querySelector(".sim-dot-base");
    var bb = sampleAt(baseline, a.t);
    if (bb) { db.setAttribute("cx", cx); db.setAttribute("cy", geom.y(bb.T)); db.removeAttribute("visibility"); }
    else db.setAttribute("visibility", "hidden");
    tip.innerHTML = "<b>" + a.t.toFixed(1) + " min</b>" +
      "<span>Your settings <b>" + a.T.toFixed(1) + " °C</b></span>" +
      (bb ? "<span>Default settings <b>" + bb.T.toFixed(1) + " °C</b></span>" : "") +
      "<span>State of charge <b>" + (a.soc * 100).toFixed(0) + "%</b></span>";
    tip.hidden = false;
    var left = cx + 12;
    if (left + tip.offsetWidth > geom.W - 4) left = cx - 12 - tip.offsetWidth;
    tip.style.left = Math.max(0, left) + "px";
    tip.style.top = Math.max(0, Math.min(geom.H - tip.offsetHeight - 4, geom.y(a.T) - tip.offsetHeight - 10)) + "px";
  }
  function hideHover() {
    var g = plot.querySelector(".sim-hover");
    if (g) g.setAttribute("visibility", "hidden");
    tip.hidden = true;
  }

  // ---- readouts ----
  function stat(label, value, extra) {
    return "<div><dt>" + label + "</dt><dd>" + value + "</dd>" + (extra ? '<p class="sim-flag">' + extra + "</p>" : "") + "</div>";
  }
  function update() {
    CONTROLS.forEach(function (c) {
      outputs[c.key].textContent = state[c.key].toFixed(c.digits) + " " + c.unit;
    });
    var same = CONTROLS.every(function (c) { return state[c.key] === c.def; });
    live = same ? baseline : simulate(state);
    var over = live.peakT > LIMIT_C;
    stats.innerHTML =
      stat("Peak cell temperature", live.peakT.toFixed(1) + " °C", over ? "&#9888; Over the 60 °C limit" : "") +
      stat("Charge left at the finish", (live.finalSoc * 100).toFixed(0) + "%",
        live.depletedAt !== null ? "&#9888; Cell empty at " + live.depletedAt.toFixed(1) + " min" : "") +
      stat("Peak cell current", live.peakI.toFixed(1) + " A", "");
    var d = live.peakT - baseline.peakT;
    note.textContent = same
      ? "Drag a slider to change an assumption. The dashed line keeps the default result for comparison."
      : "Peak temperature is " + Math.abs(d).toFixed(1) + " °C " + (d >= 0 ? "higher" : "lower") +
        " than with the default settings (" + baseline.peakT.toFixed(1) + " °C).";
    reset.disabled = same;
    hideHover();
    draw();
  }

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(draw, 100);
  });
  update();
})();
