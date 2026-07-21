/* Interactive figures for the book — dependency-free, offline, no CDN.
 *
 * Each `<figure class="widget" data-widget="NAME">` in a chapter is wired up on
 * load by the matching entry in WIDGETS below. A widget builds a responsive
 * hi-DPI canvas plus its controls inside the figure (before the <figcaption>),
 * and redraws on input and on resize.
 *
 * TO ADD A WIDGET: write a WIDGETS["your-name"] = function (figure, cap) { ... }
 * using the helpers below, then reference it from a chapter with
 *   <figure class="widget" data-widget="your-name"><figcaption>...</figcaption></figure>
 * The build numbers and captions it like any other figure; the runtime injects
 * the canvas and controls above the caption.
 *
 * The one widget shipped here ("example-slider") is a worked example — delete it
 * and replace it with figures that fit your book, keeping the helpers above it.
 *
 * Colors mirror assets/style.css. Keep them in sync with the :root palette.
 */
(function () {
  "use strict";

  var C = {
    ink: "#17181b",
    inkSoft: "#3b3d42",
    muted: "#6a6d73",
    rule: "#e4e3dd",
    ruleStrong: "#cfcdc4",
    accent: "#274b6d",
    accentSoft: "#eaf0f6",
    amber: "#9c6b12",
    grid: "#ededea",
  };

  // A responsive hi-DPI canvas inserted into `parent` before `before`.
  function makeCanvas(parent, before, heightRatio) {
    var canvas = document.createElement("canvas");
    canvas.className = "widget-canvas";
    parent.insertBefore(canvas, before);
    var ctx = canvas.getContext("2d");
    function size() {
      var cssW = canvas.clientWidth || parent.clientWidth || 600;
      var cssH = Math.round(cssW * heightRatio);
      var dpr = window.devicePixelRatio || 1;
      canvas.style.height = cssH + "px";
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { w: cssW, h: cssH };
    }
    return { canvas: canvas, ctx: ctx, size: size };
  }

  // A control row (slider + live label) appended into `parent` before `before`.
  function addSlider(parent, before, label, min, max, step, value) {
    var row = document.createElement("label");
    row.className = "widget-slider";
    var name = document.createElement("span");
    name.className = "widget-slider-label";
    name.innerHTML = label;
    var input = document.createElement("input");
    input.type = "range";
    input.min = min;
    input.max = max;
    input.step = step;
    input.value = value;
    row.appendChild(name);
    row.appendChild(input);
    parent.insertBefore(row, before);
    return input;
  }

  function controlsBox(parent, before) {
    var box = document.createElement("div");
    box.className = "widget-controls";
    parent.insertBefore(box, before);
    return box;
  }

  function readoutBox(parent, before) {
    var box = document.createElement("div");
    box.className = "widget-readout";
    parent.insertBefore(box, before);
    return box;
  }

  // Faint gridlines plus the x/y axes for a world-to-pixel mapping.
  function drawAxes(ctx, dim, mx, my, xr, yr) {
    ctx.clearRect(0, 0, dim.w, dim.h);
    ctx.lineWidth = 1;
    ctx.strokeStyle = C.grid;
    var i;
    for (i = Math.ceil(xr[0]); i <= Math.floor(xr[1]); i++) {
      ctx.beginPath();
      ctx.moveTo(mx(i), 0);
      ctx.lineTo(mx(i), dim.h);
      ctx.stroke();
    }
    for (i = Math.ceil(yr[0]); i <= Math.floor(yr[1]); i++) {
      ctx.beginPath();
      ctx.moveTo(0, my(i));
      ctx.lineTo(dim.w, my(i));
      ctx.stroke();
    }
    ctx.strokeStyle = C.ruleStrong;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, my(0));
    ctx.lineTo(dim.w, my(0));
    ctx.moveTo(mx(0), 0);
    ctx.lineTo(mx(0), dim.h);
    ctx.stroke();
  }

  // Stroke y = f(x) across the visible x-range.
  function plotFn(ctx, mx, my, xr, f, color, width) {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineJoin = "round";
    ctx.beginPath();
    var n = 240;
    for (var i = 0; i <= n; i++) {
      var x = xr[0] + ((xr[1] - xr[0]) * i) / n;
      var px = mx(x);
      var py = my(f(x));
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();
  }

  function dot(ctx, x, y, r, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  function fmt(v) {
    return (v >= 0 ? " " : "") + v.toFixed(2);
  }

  var WIDGETS = {};

  // ---- Example widget (delete or replace) --------------------------------
  // A parabola y = a x^2 whose curvature the reader controls with a slider.
  // This exists to show the pattern: build a canvas + a slider, then redraw on
  // input. Copy it, rename it, and make it illustrate something in your book.
  WIDGETS["example-slider"] = function (figure, cap) {
    var xr = [-2, 2];
    var yr = [-8.5, 8.5];
    var cv = makeCanvas(figure, cap, 0.6);
    var controls = controlsBox(figure, cap);
    var readout = readoutBox(figure, cap);
    var aInput = addSlider(controls, null, "coefficient&nbsp;<em>a</em>", -2, 2, 0.1, 1);

    function draw() {
      var dim = cv.size();
      var pad = 8;
      var mx = function (x) {
        return pad + ((x - xr[0]) * (dim.w - 2 * pad)) / (xr[1] - xr[0]);
      };
      var my = function (y) {
        return dim.h - pad - ((y - yr[0]) * (dim.h - 2 * pad)) / (yr[1] - yr[0]);
      };
      var ctx = cv.ctx;
      var a = parseFloat(aInput.value);
      drawAxes(ctx, dim, mx, my, xr, yr);
      plotFn(
        ctx,
        mx,
        my,
        xr,
        function (x) {
          return a * x * x;
        },
        C.accent,
        2.5
      );
      dot(ctx, mx(0), my(0), 5, C.amber);
      readout.innerHTML =
        '<span class="widget-num">y = a x²,  a = ' + fmt(a) + "</span>";
    }

    aInput.addEventListener("input", draw);
    window.addEventListener("resize", draw);
    draw();
  };
  // ---- End example widget ------------------------------------------------

  function boot() {
    var figures = document.querySelectorAll("figure.widget[data-widget]");
    Array.prototype.forEach.call(figures, function (figure) {
      var name = figure.getAttribute("data-widget");
      var builder = WIDGETS[name];
      if (!builder) return;
      var cap = figure.querySelector("figcaption");
      builder(figure, cap);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
