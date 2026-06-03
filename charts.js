/* ============================================================
   INDUSTRIAS SANCHIA — SVG chart renderers (no dependencies)
   Each fn returns an <svg> string sized by viewBox; CSS scales it.
   ============================================================ */
(function () {
  const C = window.SANCHIA.COLORS;
  const FMONO = "font-family:'IBM Plex Mono',monospace";

  function niceMax(v) {
    const steps = [1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200];
    const target = v * 1.12;
    const mag = Math.pow(10, Math.floor(Math.log10(target)));
    for (const s of steps) { if (s * mag >= target) return s * mag; }
    return 10 * mag;
  }

  function yAxis(max, ticks, x0, x1, top, bottom) {
    let g = '';
    for (let i = 0; i <= ticks; i++) {
      const val = (max / ticks) * i;
      const y = bottom - (bottom - top) * (i / ticks);
      g += `<line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="${C.line}" stroke-width="1"/>`;
      g += `<text x="${x0 - 9}" y="${y + 3.5}" text-anchor="end" style="${FMONO};font-size:10px;fill:${C.muted}">${(+val.toFixed(1))}</text>`;
    }
    return g;
  }

  /* ---------- Stacked vertical bars ---------- */
  function stackedBar(data, series, opts = {}) {
    const W = 720, H = 320, top = 22, bottom = 268, left = 42, right = 14;
    const max = niceMax(Math.max(...data.map(d => series.reduce((s, k) => s + d[k.key], 0))));
    const plotW = W - left - right;
    const n = data.length;
    const band = plotW / n;
    const bw = Math.min(46, band * 0.56);
    let bars = '';
    data.forEach((d, i) => {
      const cx = left + band * i + band / 2;
      let yCur = bottom;
      series.forEach(s => {
        const h = (d[s.key] / max) * (bottom - top);
        yCur -= h;
        bars += `<rect x="${cx - bw / 2}" y="${yCur}" width="${bw}" height="${h}" fill="${s.color}" rx="2"><title>${s.label}: ${d[s.key].toFixed(1)} h</title></rect>`;
      });
      const total = series.reduce((s, k) => s + d[k.key], 0);
      bars += `<text x="${cx}" y="${yCur - 7}" text-anchor="middle" style="font-family:Archivo,sans-serif;font-weight:700;font-size:11px;fill:${C.navy}">${total.toFixed(1)}</text>`;
      bars += `<text x="${cx}" y="${bottom + 17}" text-anchor="middle" style="${FMONO};font-size:10.5px;fill:${C.muted}">${d[opts.xkey || 'maquina']}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img">
      ${yAxis(max, 5, left, W - right, top, bottom)}${bars}
      <line x1="${left}" y1="${bottom}" x2="${W - right}" y2="${bottom}" stroke="${C.muted}" stroke-width="1"/>
    </svg>`;
  }

  /* ---------- Simple vertical bars ---------- */
  function bars(data, opts = {}) {
    const W = 720, H = 300, top = 22, bottom = 250, left = 42, right = 14;
    const color = opts.color || C.navy;
    const max = niceMax(Math.max(...data.map(d => d.v)));
    const plotW = W - left - right, band = plotW / data.length, bw = Math.min(44, band * 0.5);
    let g = '';
    data.forEach((d, i) => {
      const cx = left + band * i + band / 2;
      const h = (d.v / max) * (bottom - top);
      g += `<rect x="${cx - bw / 2}" y="${bottom - h}" width="${bw}" height="${h}" fill="${color}" rx="3"><title>${d.k}: ${d.v}</title></rect>`;
      g += `<text x="${cx}" y="${bottom - h - 7}" text-anchor="middle" style="font-family:Archivo,sans-serif;font-weight:700;font-size:11px;fill:${color}">${d.v}</text>`;
      g += `<text x="${cx}" y="${bottom + 17}" text-anchor="middle" style="${FMONO};font-size:10.5px;fill:${C.muted}">${d.k}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img">
      ${yAxis(max, 5, left, W - right, top, bottom)}${g}
      <line x1="${left}" y1="${bottom}" x2="${W - right}" y2="${bottom}" stroke="${C.muted}" stroke-width="1"/>
    </svg>`;
  }

  /* ---------- Area + line ---------- */
  function area(data, opts = {}) {
    const W = 720, H = 300, top = 20, bottom = 250, left = 42, right = 16;
    const color = opts.color || C.navy;
    const max = niceMax(Math.max(...data.map(d => d.h)));
    const plotW = W - left - right, n = data.length;
    const x = i => left + (plotW) * (i / (n - 1));
    const y = v => bottom - (v / max) * (bottom - top);
    let line = '', areaPts = `${x(0)},${bottom} `;
    data.forEach((d, i) => { const px = x(i), py = y(d.h); line += (i ? 'L' : 'M') + px + ' ' + py + ' '; areaPts += `${px},${py} `; });
    areaPts += `${x(n - 1)},${bottom}`;
    let dots = '', labels = '';
    data.forEach((d, i) => {
      const px = x(i), py = y(d.h);
      dots += `<circle cx="${px}" cy="${py}" r="2.6" fill="${color}"/>`;
      if (i % 3 === 0 || i === n - 1) labels += `<text x="${px}" y="${bottom + 17}" text-anchor="middle" style="${FMONO};font-size:9.5px;fill:${C.muted}">${d.d}</text>`;
    });
    return `<svg viewBox="0 0 ${W} ${H}" width="100%" preserveAspectRatio="xMidYMid meet" role="img">
      <defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="${color}" stop-opacity="0.20"/>
        <stop offset="1" stop-color="${color}" stop-opacity="0.02"/>
      </linearGradient></defs>
      ${yAxis(max, 5, left, W - right, top, bottom)}
      <polygon points="${areaPts}" fill="url(#ag)"/>
      <path d="${line}" fill="none" stroke="${color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
      ${dots}${labels}
      <line x1="${left}" y1="${bottom}" x2="${W - right}" y2="${bottom}" stroke="${C.muted}" stroke-width="1"/>
    </svg>`;
  }

  /* ---------- Donut ---------- */
  function donut(data, opts = {}) {
    const S = 230, cx = S / 2, cy = S / 2, r = 86, sw = 30;
    const total = data.reduce((s, d) => s + d.value, 0);
    const circ = 2 * Math.PI * r;
    let off = 0, segs = '';
    data.forEach(d => {
      const frac = d.value / total;
      const len = frac * circ;
      segs += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${d.color}" stroke-width="${sw}"
        stroke-dasharray="${len} ${circ - len}" stroke-dashoffset="${-off}" transform="rotate(-90 ${cx} ${cy})"><title>${d.name}: ${d.value.toFixed(1)} h</title></circle>`;
      off += len;
    });
    return `<svg viewBox="0 0 ${S} ${S}" width="100%" style="max-width:230px;margin:0 auto;display:block" role="img">
      ${segs}
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" style="font-family:Archivo,sans-serif;font-weight:800;font-size:30px;fill:${C.navy}">${(+total.toFixed(0))}</text>
      <text x="${cx}" y="${cy + 16}" text-anchor="middle" style="${FMONO};font-size:10px;letter-spacing:0.1em;fill:${C.muted}">HORAS TOTAL</text>
    </svg>`;
  }

  /* ---------- Horizontal bars list (in HTML, not svg) ---------- */
  function hbars(rows, opts = {}) {
    const max = Math.max(...rows.map(r => r.v));
    const color = opts.color || C.navy;
    return rows.map(r => `
      <div class="rowlist__item">
        <span class="rowlist__name">${r.k}</span>
        <span class="rowlist__val">${r.label || r.v}</span>
        <span class="rowlist__track"><i style="width:${Math.max(4, (r.v / max) * 100)}%;background:${r.color || color}"></i></span>
      </div>`).join('');
  }

  window.CHART = { stackedBar, bars, area, donut, hbars };
})();
