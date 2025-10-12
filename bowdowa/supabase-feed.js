async function fetchListings(){
  try{
    const r = await fetch("/api/listings",{cache:"no-store"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }catch(e){ console.error("Listings fetch error:", e); return []; }
}
function money(v, wal="PLN"){ if(v==null) return ""; try{ return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); } catch { return `${v} ${wal}`; } }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstElementChild; }

function looksLikeGrid(node){
  const cs = getComputedStyle(node);
  return cs.display==="grid" || cs.display==="flex";
}
function countCards(node){
  return Array.from(node.querySelectorAll("a,button")).filter(b=>/szczeg|szczegóły/i.test(b.textContent||"")).length;
}
function findListingContainers(){
  // szukaj po przyciskach "Szczegóły" i idź w górę do kontenera z wieloma kartami
  const found = new Set();
  const candidates = [];

  Array.from(document.querySelectorAll("a,button")).forEach(btn=>{
    if(!/szczeg|szczegóły/i.test(btn.textContent||"")) return;
    let cur = btn.closest("article,li,div") || btn.parentElement;
    for(let i=0;i<7 && cur; i++){
      if(looksLikeGrid(cur) && cur.children.length>=3 && countCards(cur)>=3){
        if(!found.has(cur)){ found.add(cur); candidates.push(cur); }
      }
      cur = cur.parentElement;
    }
  });

  if(!candidates.length){
    // fallback: największy grid/flex w <main> z wieloma "Szczegóły"
    const main = document.querySelector("main") || document;
    const grids = Array.from(main.querySelectorAll("section,div,ul"))
      .filter(n=>looksLikeGrid(n) && n.children.length>=3 && countCards(n)>=3)
      .sort((a,b)=>b.clientWidth*b.clientHeight - a.clientWidth*a.clientHeight);
    if(grids[0]) candidates.push(grids[0]);
  }
  return candidates;
}

function renderCards(list){
  return list.map(x=>{
    const img = Array.isArray(x.zdjecia)&&x.zdjecia[0] ? x.zdjecia[0] : "https://placehold.co/640x360?text=Brak+zdjecia";
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

function cleanupOldDynamic(){
  document.querySelectorAll(".vis-dyn-grid,#dynamic-listings-root,[data-mock-list='true']").forEach(n=>{
    // usuń stare dynamiczne kontenery, jeśli były
    if(n.classList.contains("vis-dyn-grid")) n.remove();
    if(n.id==="dynamic-listings-root") n.remove();
  });
}

async function replaceAllListings(){
  const containers = findListingContainers();
  if(!containers.length) return;
  const data = await fetchListings();

  cleanupOldDynamic();

  containers.forEach(container=>{
    container.setAttribute("data-mock-list","true");
    container.innerHTML = ""; // wyczyść mockowe karty

    const grid = document.createElement("div");
    grid.className = "vis-dyn-grid";
    grid.style.display = "grid";
    grid.style.gridTemplateColumns = "repeat(auto-fill,minmax(260px,1fr))";
    grid.style.gap = "16px";

    if(Array.isArray(data) && data.length){
      renderCards(data).forEach(card=>grid.appendChild(card));
    }else{
      grid.appendChild(el(`<div style="padding:24px;border:1px dashed #30363d;border-radius:12px;color:#9aa4b2;background:#0f1217">Brak ogłoszeń w bazie Supabase.</div>`));
    }
    container.appendChild(grid);
  });
}

/* Reaguj na SPA (pushState/replaceState/popstate) i klik w linki */
function onRoute(){
  const p = location.pathname;
  if (p === "/" || /^\/ogloszenia(\/|$)/.test(p)) {
    // poczekaj chwilę aż SPA wyrenderuje DOM
    setTimeout(replaceAllListings, 50);
    const obs = new MutationObserver((m, o)=>{
      // jeśli w trakcie SPA pojawi się kontener – podmień
      if(findListingContainers().length){ replaceAllListings(); o.disconnect(); }
    });
    obs.observe(document, {childList:true, subtree:true});
    setTimeout(()=>obs.disconnect(), 5000);
  }
}

(function(){
  ["pushState","replaceState"].forEach(fn=>{
    const orig = history[fn];
    history[fn] = function(){ const r=orig.apply(this, arguments); window.dispatchEvent(new Event("locationchange")); return r; };
  });
  window.addEventListener("popstate", ()=>window.dispatchEvent(new Event("locationchange")));
  window.addEventListener("locationchange", onRoute);

  // klik w link w obrębie tej samej domeny
  document.addEventListener("click", e=>{
    const a = e.target && e.target.closest && e.target.closest("a[href]");
    if(!a) return;
    const href = a.getAttribute("href"); if(!href) return;
    try{
      const u = new URL(href, location.href);
      if(u.origin === location.origin) setTimeout(onRoute, 50);
    }catch(_){}
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onRoute);
  } else {
    onRoute();
  }
})();
