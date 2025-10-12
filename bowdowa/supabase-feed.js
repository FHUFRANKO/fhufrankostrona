async function fetchListings(){
  try{
    const r = await fetch("/api/listings",{cache:"no-store"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }catch(e){ console.error("Listings fetch error:", e); return []; }
}
function money(v, wal="PLN"){ if(v==null) return ""; try{ return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); } catch { return `${v} ${wal}`; } }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstElementChild; }

/* Znajdź największy grid/listę kart w obrębie strony */
function findGrid(ctx=document){
  const main = ctx.querySelector("main") || ctx;
  // najpierw sekcja z nagłówkiem „Busy i samochody…” lub „Ogłoszenia”
  const hint = Array.from(main.querySelectorAll("h1,h2,h3")).find(h=>/busy|samochody|ogłoszenia|ogloszenia/i.test(h.textContent||""));
  if(hint){
    let n=hint; for(let i=0;i<7&&n;i++){ n=n.parentElement; if(!n) break;
      const cs=getComputedStyle(n);
      if(cs.display==="grid"||cs.display==="flex") return n;
    }
  }
  // fallback: największy grid/flex
  const grids = Array.from(main.querySelectorAll("section,div,ul"))
    .filter(x=>["grid","flex"].includes(getComputedStyle(x).display));
  return grids.sort((a,b)=>b.clientWidth*b.clientHeight - a.clientWidth*a.clientHeight)[0] || null;
}

function renderCards(list){
  return list.map(x=>{
    const img = Array.isArray(x.zdjecia)&&x.zdjecia[0]?x.zdjecia[0]:"https://placehold.co/640x360?text=Brak+zdjecia";
    const cechy = Array.isArray(x.cechy)?x.cechy.slice(0,6).join(" • "):"";
    return el(`
      <article class="vis-card" style="background:#13161b;border:1px solid #1f232a;border-radius:12px;overflow:hidden">
        <div style="aspect-ratio:16/9;background:#0e1116"><img src="${img}" alt="${x.tytul||""}" style="width:100%;height:100%;object-fit:cover"></div>
        <div style="padding:12px">
          <h3 style="margin:0 0 8px;font-size:18px;color:#fff">${x.tytul||"Ogłoszenie"}</h3>
          <p style="margin:0 0 6px;color:#9aa4b2;font-size:13px">${x.lokalizacja||""}</p>
          <p style="margin:0 0 8px;font-weight:700">${money(x.cena, x.waluta||"PLN")}</p>
          ${cechy?`<p style="margin:0;color:#9aa4b2;font-size:12px">${cechy}</p>`:""}
        </div>
      </article>
    `);
  });
}

async function replaceOnPage(){
  // czekaj aż pojawi się grid (SPA może dociągać HTML)
  const start = Date.now();
  let grid = findGrid();
  if(!grid){
    await new Promise(resolve=>{
      const obs = new MutationObserver(()=>{
        grid = findGrid();
        if(grid){ obs.disconnect(); resolve(); }
        if(Date.now()-start>5000){ obs.disconnect(); resolve(); }
      });
      obs.observe(document, {childList:true, subtree:true});
      setTimeout(()=>{obs.disconnect(); resolve();}, 5000);
    });
    grid = findGrid();
  }
  if(!grid) return;

  // wyczyść mocki i wstaw prawdziwe dane
  const data = await fetchListings();
  grid.innerHTML = "";
  if(Array.isArray(data) && data.length){
    renderCards(data).forEach(card=>grid.appendChild(card));
  }else{
    grid.appendChild(el(`<div style="padding:24px;border:1px dashed #30363d;border-radius:12px;color:#9aa4b2;background:#0f1217">Brak ogłoszeń w bazie Supabase.</div>`));
  }
}

/* Obsługa SPA: reaguj na każdą zmianę adresu i klik w link */
function onRoute(){
  const p = location.pathname;
  if (p === "/" || /^\/ogloszenia(\/|$)/.test(p)) replaceOnPage();
}

(function(){
  // patch pushState/replaceState -> custom event
  ["pushState","replaceState"].forEach(fn=>{
    const orig = history[fn];
    history[fn] = function(){ const r = orig.apply(this, arguments); window.dispatchEvent(new Event("locationchange")); return r; };
  });
  window.addEventListener("popstate", ()=>window.dispatchEvent(new Event("locationchange")));
  window.addEventListener("locationchange", ()=>setTimeout(onRoute, 0));

  // klik w dowolny link tego samego originu
  document.addEventListener("click", e=>{
    const a = e.target && e.target.closest && e.target.closest("a[href]");
    if(!a) return;
    try{
      const u = new URL(a.getAttribute("href"), location.href);
      if(u.origin === location.origin) setTimeout(onRoute, 50);
    }catch(_){}
  });

  // pierwsze uruchomienie
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onRoute);
  } else {
    onRoute();
  }
})();
