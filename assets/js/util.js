// Shared helpers for every calculator page: safe localStorage, number formatting, copy-to-clipboard, small DOM helpers.
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

  // Colours an element green/red by the sign of n
  function setSign(el, n){
    el.classList.toggle('profit', n > 0);
    el.classList.toggle('loss', n < 0);
  }

  // Greys out the cards that contain the given element ids while the inputs are empty/invalid
  function setEmpty(ids, on){
    ids.forEach(id => document.getElementById(id).closest('.card').classList.toggle('is-empty', on));
  }

  // Centres a gauge label under its marker at p % of #gaugeTrack, keeping it inside the track
  function positionLabel(el, p){
    const trackW = document.getElementById('gaugeTrack').clientWidth;
    el.style.transform = 'none';
    el.style.left = '0px';
    const w = el.offsetWidth;
    el.style.left = Math.max(0, Math.min(trackW - w, p / 100 * trackW - w / 2)) + 'px';
  }

  return { store, fmt, copyText, setSign, setEmpty, positionLabel };
})();
