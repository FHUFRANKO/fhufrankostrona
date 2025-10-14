(function(){
  if(!/\/ogloszenia(?:\/|$)/.test(location.pathname)) return;

  // policz faktyczne karty ogłoszeń
  function realCount(){
    const selectors = [
      'article[data-ad]', '.ad-card', '.listing-card', 'article.card', 'li[data-id]',
      '[data-testid*="card"]', 'a[href*="/ogloszenie/"]'
    ];
    for(const s of selectors){
      const n = document.querySelectorAll(s).length;
      if(n>0) return n;
    }
    return 0;
  }

  // prosta odmiana "bus"
  function busWord(n){
    const m10 = n % 10, m100 = n % 100;
    if(n === 1) return 'bus';
    if(m10>=2 && m10<=4 && !(m100>=12 && m100<=14)) return 'busy';
    return 'busów';
  }

  function update(){
    const total = realCount();

    // 1) Znajdź nagłówek sekcji i jego kontener
    const heading = [...document.querySelectorAll('h1,h2')].find(h =>
      /Busy i samochody dostawcze/i.test((h.textContent||'').trim())
    );
    const root = heading ? (heading.closest('section') || heading.parentElement || document) : document;

    // 2) Znajdź "chip" z liczbą (np. 50 busów) — zwykle to DIV/SPAN obok nagłówka
    const candidates = [...root.querySelectorAll('span,div,p,strong,em')];
    let chip = null;
    for(const el of candidates){
      const txt = (el.textContent||'').trim();
      if(/\b\d+\s+bus\w*/i.test(txt)){
        // nie bierzemy chipów z filtrów nad sekcją
        const isQuick = el.closest('section,div') && /Szybkie filtry/i.test(el.closest('section,div').textContent||'');
        if(!isQuick && (heading ? el.compareDocumentPosition(heading)&Node.DOCUMENT_POSITION_FOLLOWING : true)){
          chip = el; break;
        }
      }
    }

    if(chip){
      if(total>0){
        chip.textContent = total+' '+busWord(total);
        chip.style.display = '';
      }else{
        // przy braku wyników chowamy licznik
        chip.style.display = 'none';
      }
    }

    // 3) Ukryj "Szybkie filtry" (bo mają fałszywe liczby)
    const quick = [...document.querySelectorAll('section,div')]
      .find(x => /Szybkie filtry/i.test((x.textContent||'')));
    if(quick) quick.style.display = 'none';

    // 4) Gdy 0 wyników — schowaj paginację/sort/przełącznik widoku
    if(total === 0){
      document.querySelectorAll(
        '[aria-label*="Sortuj"],[data-sort],.pagination,nav[aria-label*="pagina"],[class*="pagination"],[data-view-toggle]'
      ).forEach(el => (el.closest('nav,div,section')||el).style.display='none');
    }
  }

  update();
  new MutationObserver(update).observe(document.documentElement,{childList:true,subtree:true});
  window.addEventListener('load', update);
})();
