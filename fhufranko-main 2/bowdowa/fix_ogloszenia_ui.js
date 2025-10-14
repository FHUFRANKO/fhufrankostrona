(function(){
  if(!/\/ogloszenia/.test(location.pathname)) return;

  function countCards(){
    // policz faktyczne kafelki ogłoszeń w siatce
    const selectors = [
      'main .listing-card',
      'main article',
      'main a[href*="/ogloszenia/"]',
      'main [class*="card"]',
      'main [role="list"] > *',
      'main .grid > *'
    ];
    for (const sel of selectors){
      const n = document.querySelectorAll(sel).length;
      if (n > 0) return n;
    }
    return 0;
  }

  function fix(){
    const n = countCards();

    // 1) Nagłówek: "Busy i samochody dostawcze 50 busów" -> realna liczba
    const nodes = Array.from(document.querySelectorAll('h1,h2,span,div,small,strong'));
    nodes.forEach(el=>{
      const t = (el.textContent||'').trim();
      if (/busów/i.test(t) && /\d+/.test(t)) {
        el.textContent = t.replace(/\d+/, String(n));
      }
    });

    // 2) Usuń liczby w nawiasach przy filtrach: "Do 3.5t (32)" -> "Do 3.5t"
    document.querySelectorAll('button,a,.chip,.badge,li,span,div').forEach(el=>{
      el.childNodes.forEach(nd=>{
        if(nd.nodeType===3){ nd.nodeValue = nd.nodeValue.replace(/\s*\(\d+\)\s*/g,' '); }
      });
    });

    // 3) Wyłącz/ukryj „Szybkie filtry” (skoro liczby nie są wiarygodne)
    const quick = Array.from(document.querySelectorAll('section,div')).find(x=>/Szybkie filtry/i.test(x.textContent||''));
    if (quick) quick.style.display = 'none';

    // 4) Przy 0 wyników ukryj paginację i widok siatka/lista
    if (n === 0){
      document.querySelectorAll('.pagination, nav[aria-label="pagination"], [data-testid="pagination"]').forEach(e=>e.style.display='none');
      document.querySelectorAll('[aria-label="grid"],[aria-label="list"]').forEach(e=>e.style.display='none');
    }

    // 5) Przycisk "Szukaj (0)" -> "Szukaj"
    Array.from(document.querySelectorAll('button')).forEach(b=>{
      if(/\bSzukaj\b/i.test(b.textContent||'')) b.textContent = 'Szukaj';
    });
  }

  fix();
  new MutationObserver(fix).observe(document.documentElement,{childList:true,subtree:true});
  window.addEventListener('load', fix);
})();
