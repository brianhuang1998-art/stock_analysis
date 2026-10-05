// Site chrome shared by every page: the 全部工具 dropdown (with search) in the top bar, footer, back-to-top, offline cache.
// The pages, categories and keywords all come from site-config.js; the top bar itself and the breadcrumb are written
// into each page by _dev/build.py.
(function(){
  const SITE = self.SITE;
  if(!SITE) return;
  const REPO = SITE.repo;
  const TOOL_MENU = [SITE.home].map(h => ({ title: h.title, href: h.href, keywords: h.keywords, items: [] })).concat(
    SITE.categories.map(c => ({
      title: c.title, href: c.href, keywords: c.keywords, soon: c.soon,
      items: c.tools.filter(t => !t.soon && t.href)
    }))
  );

  const topbar = document.querySelector('.topbar');
  if(!topbar) return;
  const current = location.pathname.split('/').pop() || './';

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
      '<p class="footer-updated">最後更新：<time id="lastUpdated">讀取中…</time></p>' +
    '</div>';
  const main = document.querySelector('main');
  if(main) main.after(footer); else document.body.appendChild(footer);

  /* ---------- back to top (floating button on phones) ---------- */
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function toTop(){ window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }); }
  const toTopBtn = document.createElement('button');
  toTopBtn.id = 'backToTop';
  toTopBtn.type = 'button';
  toTopBtn.setAttribute('aria-label', '回到頂部');
  toTopBtn.textContent = '↑';
  toTopBtn.addEventListener('click', toTop);
  document.body.appendChild(toTopBtn);
  function syncToTop(){ toTopBtn.classList.toggle('show', window.scrollY > 400); }
  window.addEventListener('scroll', syncToTop, { passive: true });
  syncToTop();

  /* ---------- PWA: offline cache (needs https or localhost) ---------- */
  if('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')){
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }

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
