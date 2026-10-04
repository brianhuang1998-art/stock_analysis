// Shared helpers for every calculator page: safe localStorage, number formatting, copy-to-clipboard.
// Loaded in <head> (via the BUILD:HEAD block), so page scripts can use Util right away.
window.Util = (function(){
  const store = {
    get(key){ try { return localStorage.getItem(key); } catch(e){ return null; } },
    set(key, value){ try { localStorage.setItem(key, value); } catch(e){} },
    getJSON(key){ try { return JSON.parse(localStorage.getItem(key)); } catch(e){ return null; } },
    setJSON(key, value){ try { localStorage.setItem(key, JSON.stringify(value)); } catch(e){} }
  };

  const fmt = {
    int: n => Math.round(n).toLocaleString('zh-Hant-TW'),
    money: n => fmt.int(n) + ' 元',
    price: n => n.toFixed(2) + ' 元',
    signedMoney: n => (Math.round(n) > 0 ? '+' : '') + fmt.money(n),
    pct: (n, digits) => (n >= 0 ? '+' : '') + n.toFixed(digits === undefined ? 2 : digits) + '%'
  };

  function fallbackCopy(text, done){
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch(e){}
    document.body.removeChild(ta);
    done();
  }

  // Copies text and flashes "已複製 ✓" on the button for 1.5 s
  function copyText(text, btn){
    const original = btn.textContent;
    const done = () => {
      btn.textContent = '已複製 ✓';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = original;
        btn.classList.remove('copied');
      }, 1500);
    };
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
    } else {
      fallbackCopy(text, done);
    }
  }

  return { store, fmt, copyText };
})();
