// Site chrome shared by every page: merged top bar (brand + breadcrumb + 全部工具/搜尋), footer, back-to-top.
// Edit TOOL_MENU here when adding a page.
(function(){
  const REPO = 'brianhuang1998-art/stock_analysis';
  const TOOL_MENU = [
    { title: '首頁', href: 'home_page.html', keywords: 'home 回首頁', items: [] },
    { title: '試算工具', href: 'tools.html', keywords: '損益 手續費 證交稅', items: [
      { title: 'ETF 試算', href: 'etf_calculator.html', keywords: 'etf 債券 股票型 主動式 損益 兩平' },
      { title: '個股試算', href: 'stock_calculator.html', keywords: '個股 當沖 損益 兩平' },
      { title: '目標%數試算', href: 'target_price_calculator.html', keywords: '目標價 漲跌幅 升降單位 掛單' },
      { title: '加權平均成本法試算', href: 'avg_cost_calculator.html', keywords: '均價 攤平 分批 平均成本' }
    ]},
    { title: '交易與部位管理', href: 'trading_position.html', keywords: '部位 停損 再平衡', items: [
      { title: '定期定額複利試算', href: 'dca_calculator.html', keywords: 'dca 複利 存股 每月扣款 年化報酬' }
    ]},
    { title: '估值與基本面分析', href: 'valuation_analysis.html', soon: true, keywords: '本益比 ddm dcf roe 杜邦', items: [] },
    { title: '股息與現金流規劃', href: 'dividend_cashflow.html', soon: true, keywords: '配息 股利 退休 4% 現金流', items: [] }
  ];

  const topbar = document.querySelector('.topbar');
  if(!topbar) return;
  const current = location.pathname.split('/').pop() || 'home_page.html';

  /* ---------- merge subbar (breadcrumb) into the top bar ---------- */
  const subbar = document.querySelector('.subbar');
  if(subbar){
    const crumbs = document.createElement('nav');
    crumbs.className = 'crumbs';
    crumbs.setAttribute('aria-label', '麵包屑');
    while(subbar.firstChild) crumbs.appendChild(subbar.firstChild);
    // Last crumb is the page itself; hide the earlier ones on phones via CSS
    const links = crumbs.querySelectorAll('a');
    if(links.length) links[links.length - 1].setAttribute('aria-current', 'page');
    topbar.insertBefore(crumbs, topbar.querySelector('.tool-menu'));
    subbar.remove();
  }

  /* ---------- 全部工具 dropdown with search ---------- */
  function link(text, href, className){
    const a = document.createElement('a');
    a.href = href;
    a.className = className;
    a.textContent = text;
    if(href === current){
      a.classList.add('current');
      a.setAttribute('aria-current', 'page');
    }
    return a;
  }

  const wrap = document.createElement('div');
  wrap.className = 'tool-menu';

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'tool-menu-btn';
  btn.textContent = '全部工具 ▾';
  btn.setAttribute('aria-haspopup', 'true');
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-controls', 'toolMenuPanel');

  const panel = document.createElement('div');
  panel.className = 'tool-menu-panel';
  panel.id = 'toolMenuPanel';
  panel.hidden = true;

  const search = document.createElement('input');
  search.type = 'search';
  search.className = 'tool-menu-search';
  search.placeholder = '搜尋工具（快捷鍵 /）';
  search.setAttribute('aria-label', '搜尋工具');
  search.autocomplete = 'off';

  const list = document.createElement('nav');
  list.className = 'tool-menu-list';
  list.setAttribute('aria-label', '全部工具');

  const empty = document.createElement('p');
  empty.className = 'tool-menu-empty';
  empty.textContent = '找不到符合的工具';
  empty.hidden = true;

  const entries = []; // { el, text } for every link, used by search
  TOOL_MENU.forEach(group => {
    const section = document.createElement('div');
    section.className = 'tool-menu-group';
    const head = link(group.title, group.href, 'tool-menu-head');
    if(group.soon){
      const tag = document.createElement('span');
      tag.className = 'tool-menu-soon';
      tag.textContent = '開發中';
      head.appendChild(tag);
    }
    section.appendChild(head);
    entries.push({ el: head, section, text: (group.title + ' ' + (group.keywords || '')).toLowerCase() });
    group.items.forEach(item => {
      const a = link(item.title, item.href, 'tool-menu-item');
      section.appendChild(a);
      entries.push({ el: a, section, text: (item.title + ' ' + group.title + ' ' + (item.keywords || '')).toLowerCase() });
    });
    list.appendChild(section);
  });

  function visibleLinks(){
    return entries.filter(e => !e.el.hidden).map(e => e.el);
  }

  function filter(){
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    entries.forEach(e => {
      const hit = !q || q.split(/\s+/).every(w => e.text.includes(w));
      e.el.hidden = !hit;
      if(hit) shown++;
    });
    // Hide a group's divider when everything in it is filtered out
    list.querySelectorAll('.tool-menu-group').forEach(g => {
      g.hidden = !g.querySelector('a:not([hidden])');
    });
    empty.hidden = shown > 0;
  }

  search.addEventListener('input', filter);
  search.addEventListener('keydown', e => {
    if(e.key === 'Enter'){
      const first = visibleLinks()[0];
      if(first){ e.preventDefault(); location.href = first.href; }
    } else if(e.key === 'ArrowDown'){
      const first = visibleLinks()[0];
      if(first){ e.preventDefault(); first.focus(); }
    }
  });
  list.addEventListener('keydown', e => {
    if(e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
    const items = visibleLinks();
    const i = items.indexOf(document.activeElement);
    if(i < 0) return;
    e.preventDefault();
    if(e.key === 'ArrowDown') (items[i + 1] || items[i]).focus();
    else if(i === 0) search.focus();
    else items[i - 1].focus();
  });

  function setOpen(open){
    panel.hidden = !open;
    btn.setAttribute('aria-expanded', String(open));
    btn.textContent = open ? '全部工具 ▴' : '全部工具 ▾';
    if(open){
      // Don't pop the on-screen keyboard on touch devices
      if(window.matchMedia('(pointer:fine)').matches) search.focus();
    } else {
      search.value = '';
      filter();
    }
  }

  btn.addEventListener('click', e => {
    e.stopPropagation();
    setOpen(panel.hidden);
  });
  document.addEventListener('click', e => {
    if(!panel.hidden && !wrap.contains(e.target)) setOpen(false);
  });
  document.addEventListener('keydown', e => {
    if(e.key === 'Escape' && !panel.hidden){
      setOpen(false);
      btn.focus();
      return;
    }
    // "/" or Ctrl/⌘+K opens the search from anywhere except while typing in a field
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if((e.key === '/' && !typing && !e.ctrlKey && !e.metaKey && !e.altKey) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')){
      e.preventDefault();
      if(panel.hidden) setOpen(true); else search.focus();
    }
  });

  panel.append(search, list, empty);
  wrap.append(btn, panel);
  topbar.appendChild(wrap);

  /* ---------- footer ---------- */
  const footer = document.createElement('footer');
  footer.className = 'site-footer';
  footer.innerHTML =
    '<div class="footer-inner">' +
      '<nav class="footer-links" aria-label="頁尾連結">' +
        '<a href="home_page.html">🏠 回首頁</a>' +
        '<a href="#top" id="footerTop">↑ 回到頂部</a>' +
      '</nav>' +
      '<p class="footer-updated">最後更新：<time id="lastUpdated">讀取中…</time></p>' +
    '</div>';
  const main = document.querySelector('main');
  if(main) main.after(footer); else document.body.appendChild(footer);

  /* ---------- back to top (floating button on phones + footer link) ---------- */
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function toTop(){ window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }); }
  const toTopBtn = document.createElement('button');
  toTopBtn.id = 'backToTop';
  toTopBtn.type = 'button';
  toTopBtn.setAttribute('aria-label', '回到頂部');
  toTopBtn.textContent = '↑';
  toTopBtn.addEventListener('click', toTop);
  document.body.appendChild(toTopBtn);
  document.getElementById('footerTop').addEventListener('click', e => { e.preventDefault(); toTop(); });
  function syncToTop(){ toTopBtn.classList.toggle('show', window.scrollY > 400); }
  window.addEventListener('scroll', syncToTop, { passive: true });
  syncToTop();

  /* ---------- last updated = time of the latest commit pushed to GitHub ---------- */
  const CACHE_KEY = 'site:lastCommit';
  const CACHE_MS = 10 * 60 * 1000; // GitHub API allows 60 unauthenticated calls/hour per IP
  const timeEl = document.getElementById('lastUpdated');

  function show(iso){
    const d = new Date(iso);
    if(isNaN(d)) return false;
    const parts = new Intl.DateTimeFormat('zh-TW', {
      timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(d).reduce((o, p) => { o[p.type] = p.value; return o; }, {});
    timeEl.textContent = `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}`;
    timeEl.dateTime = d.toISOString();
    return true;
  }
  function readCache(){
    try { return JSON.parse(localStorage.getItem(CACHE_KEY)); } catch(e){ return null; }
  }

  const cached = readCache();
  if(cached && show(cached.iso) && Date.now() - cached.at < CACHE_MS) return;

  fetch('https://api.github.com/repos/' + REPO + '/commits?per_page=1')
    .then(r => { if(!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => {
      const iso = data[0].commit.committer.date;
      show(iso);
      try { localStorage.setItem(CACHE_KEY, JSON.stringify({ iso, at: Date.now() })); } catch(e){}
    })
    .catch(() => {
      // Offline or rate-limited: keep the cached value if any, otherwise fall back to the file's own modified time
      if(!(cached && show(cached.iso)) && !show(document.lastModified)) timeEl.textContent = '—';
    });
})();
