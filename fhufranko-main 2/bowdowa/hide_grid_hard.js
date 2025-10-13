(()=>{ 
  if (!location.pathname.toLowerCase().includes("ogloszenia")) return;

  const isDetails = n => (n.textContent||"").trim().toLowerCase().includes("szczegóły");
  const looksLikeCard = el => {
    const t=(el.textContent||"").toLowerCase();
    return /(pln|zł|km|rocznik|netto)/.test(t) && (el.querySelector("img")||el.querySelector("picture"));
  };

  const hideOnce = () => {
    // kandydat: rodzic mający wiele „Szczegóły” lub wiele kart
    const candidates = new Map();

    // 1) po CTA
    document.querySelectorAll("a,button").forEach(btn=>{
      if(!isDetails(btn)) return;
      let n=btn;
      for(let i=0;i<8 && n && n!==document.body;i++){
        n=n.parentElement;
        if(!n) break;
        const c=[...n.children];
        const manyCards = c.length>=3 && c.filter(looksLikeCard).length>=3;
        const manyCTA = n.querySelectorAll("a,button").length >= 6 && [...n.querySelectorAll("a,button")].filter(isDetails).length >= 3;
        if(manyCards || manyCTA){ candidates.set(n,(candidates.get(n)||0)+1); }
      }
    });

    // 2) fallback: duże kontenery w main
    document.querySelectorAll("main section, main div, main ul").forEach(box=>{
      const c=[...box.children];
      if(c.length>=6 && c.filter(looksLikeCard).length>=6){ candidates.set(box,(candidates.get(box)||0)+1); }
    });

    if(!candidates.size) return false;

    // wybierz najlepszy i ukryj agresywnie
    const target=[...candidates.entries()].sort((a,b)=>b[1]-a[1])[0][0];
    target.style.setProperty("display","none","important");
    target.setAttribute("data-hidden-by","ai");
    return true;
  };

  // wielokrotne próby + MutationObserver
  let tries=0, maxTries=70; // ~20-25s
  const iv=setInterval(()=>{
    if(hideOnce() || ++tries>=maxTries){ clearInterval(iv); }
  },300);

  const mo=new MutationObserver(()=>hideOnce());
  mo.observe(document.documentElement,{childList:true,subtree:true});
})();
