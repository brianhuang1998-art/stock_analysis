// Small line chart (inline SVG, no library) with optional bands, reference lines and a hover/touch tooltip.
//
//   LineChart.draw(wrapEl, {
//     xs: [0, 1, 2, ...],                       x values (years)
//     xLabel: n => n + ' 年',                    tick text
//     yFormat: v => '…',                         axis text
//     yMax: 0.2,                                 optional; default = a "nice" max of the data. Values above it are clipped
//     bands:   [{ cls: 'band-dynamic', lo: [...], hi: [...] }],
//     hlines:  [{ value: 0.06, cls: 'hline-guard', label: '上護欄', key: 'guard' }],
//     series:  [{ cls: 's-dynamic', values: [...] }],
//     tooltip: i => '<b>…</b><br>…'              html for the point at index i
//   });
//
// Legend toggle: legend items inside .chart-legend that carry data-k switch that part of the chart on/off:
//   data-k="s0"      series 0            data-k="b0"      band 0            data-k="guard"   every hline whose key is "guard"
// The legend may be rebuilt at any time (before or after draw); the on/off state is kept per chart. At least one series stays on.
// A band with follow: <series index> also hides with that series; band.color (any CSS colour) draws it as a fade-out gradient.
//
// wrapEl must contain <svg class="chart-svg"> and <div class="chart-tip" hidden>. Colours come from styles.css (.s-*, .band-*, .hline-*).
window.LineChart = (function(){
  const NS = 'http://www.w3.org/2000/svg';
  const W = 640, H = 300, PAD = { l: 62, r: 16, t: 14, b: 30 };

  function el(name, attrs, text){
    const e = document.createElementNS(NS, name);
    Object.keys(attrs || {}).forEach(k => e.setAttribute(k, attrs[k]));
    if(text !== undefined) e.textContent = text;
    return e;
  }

  function niceMax(v){
    if(!(v > 0)) return 1;
    const exp = Math.pow(10, Math.floor(Math.log10(v)));
    const f = v / exp;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * exp;
  }

  function draw(wrap, cfg){
    const svg = wrap.querySelector('.chart-svg');
    const tip = wrap.querySelector('.chart-tip');
    svg.innerHTML = '';
    tip.hidden = true;
    wrap.__cfg = cfg;
    const hidden = wrap.__hidden || (wrap.__hidden = {});
    bindLegend(wrap);

    const xs = cfg.xs;
    const lines = cfg.series.filter((s, k) => !hidden['s' + k]).map(s => s.values);
    const bands = (cfg.bands || []).filter((b, bi) => !hidden['b' + bi] && !(b.follow !== undefined && hidden['s' + b.follow]));
    const hlines = (cfg.hlines || []).filter(h => !(h.key && hidden[h.key]));

    let dataMax = 0;
    lines.forEach(vs => vs.forEach(v => { if(isFinite(v) && v > dataMax) dataMax = v; }));
    bands.forEach(b => b.hi.forEach(v => { if(isFinite(v) && v > dataMax) dataMax = v; }));
    hlines.forEach(h => { if(h.value > dataMax) dataMax = h.value; });
    const maxY = cfg.yMax || niceMax(dataMax);
    const minX = xs[0], maxX = xs[xs.length - 1];
    const x = v => PAD.l + (maxX === minX ? 0 : (v - minX) / (maxX - minX)) * (W - PAD.l - PAD.r);
    const y = v => H - PAD.b - (Math.min(Math.max(v, 0), maxY) / maxY) * (H - PAD.t - PAD.b);
    wrap.__geom = { x, y, xs, W, PAD, nSeries: cfg.series.length };

    for(let i = 0; i <= 4; i++){
      const v = maxY * i / 4;
      svg.appendChild(el('line', { class: i === 0 ? 'axis' : 'grid', x1: PAD.l, x2: W - PAD.r, y1: y(v), y2: y(v) }));
      svg.appendChild(el('text', { x: PAD.l - 8, y: y(v) + 4, 'text-anchor': 'end' }, cfg.yFormat(v)));
    }

    // About 5 x ticks on whole numbers, plus the last one when there is room
    const span = maxX - minX;
    const step = Math.max(1, Math.ceil(span / 5));
    let lastTick = null;
    for(let v = minX; v <= maxX; v += step){
      svg.appendChild(el('text', { x: x(v), y: H - PAD.b + 18, 'text-anchor': v === minX ? 'start' : 'middle' }, cfg.xLabel(v)));
      lastTick = v;
    }
    if(lastTick !== maxX && maxX - lastTick >= step / 2){
      svg.appendChild(el('text', { x: x(maxX), y: H - PAD.b + 18, 'text-anchor': 'end' }, cfg.xLabel(maxX)));
    }

    const pts = (vs, idx) => idx.map(i => x(xs[i]).toFixed(1) + ' ' + y(vs[i]).toFixed(1));
    const all = xs.map((_, i) => i);

    const defs = el('defs');
    svg.appendChild(defs);
    bands.forEach((b, bi) => {
      const top = pts(b.hi, all).map((p, i) => (i ? 'L' : 'M') + p).join(' ');
      const bottom = pts(b.lo, all.slice().reverse()).map(p => 'L' + p).join(' ');
      const path = el('path', { class: b.cls, d: top + ' ' + bottom + ' Z' });
      if(b.color){
        const id = 'lc-grad-' + (wrap.id || 'w') + '-' + bi;
        const grad = el('linearGradient', { id, x1: 0, y1: 0, x2: 0, y2: 1 });
        grad.appendChild(el('stop', { offset: '0%', style: 'stop-color:' + b.color + ';stop-opacity:.32' }));
        grad.appendChild(el('stop', { offset: '100%', style: 'stop-color:' + b.color + ';stop-opacity:.02' }));
        defs.appendChild(grad);
        path.setAttribute('style', 'fill:url(#' + id + ');opacity:1');
      }
      svg.appendChild(path);
    });

    hlines.forEach(h => {
      svg.appendChild(el('line', { class: h.cls, x1: PAD.l, x2: W - PAD.r, y1: y(h.value), y2: y(h.value) }));
      if(h.label) svg.appendChild(el('text', { class: 'hline-label', x: W - PAD.r - 4, y: y(h.value) - 4, 'text-anchor': 'end' }, h.label));
    });

    cfg.series.forEach((s, k) => {
      if(hidden['s' + k]) return;
      svg.appendChild(el('path', { class: s.cls, d: pts(s.values, all).map((p, i) => (i ? 'L' : 'M') + p).join(' ') }));
    });

    if(!svg.__bound){
      svg.__bound = true;
      svg.addEventListener('pointermove', e => showTip(wrap, e));
      svg.addEventListener('pointerdown', e => showTip(wrap, e));
      svg.addEventListener('pointerleave', () => hideTip(wrap));
    }
  }

  // Reflect the on/off state on the legend items (called after every draw and whenever the legend is rebuilt)
  function syncLegend(wrap){
    wrap.querySelectorAll('.chart-legend [data-k]').forEach(it => {
      const off = !!wrap.__hidden[it.dataset.k];
      it.classList.toggle('off', off);
      it.setAttribute('aria-pressed', off ? 'false' : 'true');
      it.setAttribute('role', 'button');
      it.tabIndex = 0;
    });
  }

  function toggle(wrap, key){
    const cfg = wrap.__cfg;
    if(!cfg) return;
    if(/^s\d+$/.test(key) && !wrap.__hidden[key]){
      const visible = cfg.series.filter((s, i) => !wrap.__hidden['s' + i]).length;
      if(visible <= 1) return;   // keep at least one line on screen
    }
    wrap.__hidden[key] = !wrap.__hidden[key];
    draw(wrap, cfg);
  }

  function bindLegend(wrap){
    const legend = wrap.querySelector('.chart-legend');
    if(legend && !legend.__bound){
      legend.__bound = true;
      const hit = e => e.target.closest('[data-k]');
      legend.addEventListener('click', e => { const it = hit(e); if(it) toggle(wrap, it.dataset.k); });
      legend.addEventListener('keydown', e => {
        const it = hit(e);
        if(it && (e.key === 'Enter' || e.key === ' ')){ e.preventDefault(); toggle(wrap, it.dataset.k); }
      });
      new MutationObserver(() => syncLegend(wrap)).observe(legend, { childList: true });
    }
    syncLegend(wrap);
  }

  function showTip(wrap, evt){
    const cfg = wrap.__cfg, geom = wrap.__geom;
    if(!cfg) return;
    const svg = wrap.querySelector('.chart-svg');
    const tip = wrap.querySelector('.chart-tip');
    const rect = svg.getBoundingClientRect();
    const sx = (evt.clientX - rect.left) / rect.width * geom.W;
    const frac = (sx - geom.PAD.l) / (geom.W - geom.PAD.l - geom.PAD.r);
    const n = cfg.xs.length;
    const i = Math.min(n - 1, Math.max(0, Math.round(frac * (n - 1))));
    const px = geom.x(cfg.xs[i]);

    // The cursor (line + one dot per visible series) only exists while the pointer is on the chart
    let g = svg.querySelector('.cursor-group');
    if(!g){
      g = el('g', { class: 'cursor-group' });
      g.appendChild(el('line', { class: 'cursor', y1: PAD.t, y2: H - PAD.b }));
      cfg.series.forEach((s, k) => {
        if(!wrap.__hidden['s' + k]) g.appendChild(el('circle', { class: 'dot ' + s.cls, r: 4.5, 'data-i': k }));
      });
      svg.appendChild(g);
    }
    const line = g.querySelector('.cursor');
    line.setAttribute('x1', px); line.setAttribute('x2', px);
    g.querySelectorAll('.dot').forEach(c => {
      c.setAttribute('cx', px);
      c.setAttribute('cy', geom.y(cfg.series[+c.getAttribute('data-i')].values[i]));
    });

    tip.innerHTML = cfg.tooltip(i);
    tip.hidden = false;
    const wrapRect = wrap.getBoundingClientRect();
    const left = px / geom.W * rect.width + (rect.left - wrapRect.left);
    const flip = left + tip.offsetWidth + 16 > wrapRect.width;
    tip.style.left = (flip ? left - tip.offsetWidth - 10 : left + 10) + 'px';
    tip.style.top = (rect.top - wrapRect.top + 10) + 'px';
  }

  function hideTip(wrap){
    wrap.querySelector('.chart-tip').hidden = true;
    const g = wrap.querySelector('.cursor-group');
    if(g) g.remove();
  }

  function clear(wrap){
    wrap.querySelector('.chart-svg').innerHTML = '';
    wrap.querySelector('.chart-tip').hidden = true;
    wrap.__cfg = null;
  }

  return { draw, clear, niceMax };
})();
