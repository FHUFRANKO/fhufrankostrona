async function fetchListings(){
  try{
    const r = await fetch("/api/listings",{cache:"no-store"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }catch(e){ console.error("Listings fetch error:", e); return []; }
}
function money(v, wal="PLN"){ if(v==null) return ""; try{ return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); } catch { return `${v} ${wal}`; } }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstElementChild; }

/* ——— Lokalizacja właściwej SEKCJI z listą — tylko pod tymi nagłówkami ——— */
function findListingSection(){
  const labels = /(wyróżnione busy|wyroznione busy|najnowsze oferty|busy i samochody dostawcze|ogłoszenia|ogloszenia)/i;
  const heads = Array.from(document.querySelectorAll("main h1, main h2, main h3"))
    .filter(h => labels.test(h.textContent||""));
  if(!heads.length) return null;
  // najbliższy sensowny kontener (sekcja / div) – nie header/nav
  for(const h of heads){
    let n = h.parentElement;
    for(let i=0;i<5 && n;i++){
      if(["HEADER","NAV"].includes(n.tagName)) break;
      const cs = getComputedStyle(n);
      if(cs.display==="block" || cs.display==="grid" || cs.display==="flex") return {section:n, heading:h};
      n = n.parentElement;
    }
  }
  return null;
}

/* ——— Znajdź mockowy GRID tylko w TEJ sekcji — nie w całej stronie ——— */
function findMockGrid(section){
  // grid z wieloma kartami zawierającymi przycisk "Szczegóły"
  const grids = Array.from(section.querySelectorAll("section,div,ul"))
    .filter(n => {
      const cs = getComputedStyle(n);
      if(!(cs.display==="grid" || cs.display==="flex")) return false;
      const details = n.querySelectorAll("a,button");
      const hasBtns = Array.from(details).some(b => /szczeg|szczegóły/i.test(b.textContent||""));
      return hasBtns && n.children.length >= 3;
    });
  // największy kandydat
  return grids.sort((a,b)=>b.clientWidth*b.clientHeight - a.clientWidth*a.clientHeight)[0] || null;
}

/* ——— Licznik „N busów” tylko przy właściwym nagłówku ——— */
function pluralizeBus(n){
  const m10=n%10, m100=n%100;
  if(n===1) return "1 bus";
  if(m10>=2 && m10<=4 && !(m100>=12 && m100<=14)) return `${n} busy`;
  return `${n} busów`;
}
function ensureCounter(heading){
  // usuń nasze stare badge, jeśli były
  heading.parentElement.querySelectorAll(".supabase-count-badge").forEach(x=>x.remove());
  const badge = document.createElement("span");
  badge.className = "supabase-count-badge";
  badge.style.cssText = "margin-left:8px;padding:2px 8px;border-radius:999px;background:#f2f3f5;color:#111;font-size:12px;";
  heading.after(badge);
  return badge;
}

/* ——— Render kart ——— */
function renderCards(list){
  return list.map(x=>{
    const img = Array.isArray(x.zdjecia)&&x.zdjecia[0] ? x.zdjecia[0] : "https://placehold.co/640x360?text=Brak+zdjecia";
    const cechy = Array.isArray(x.cechy)?x.cechy.slice(0,6).join(" • "):"";
    return el(`
      <article style="background:#fff;border:1px solid #e6e8eb;border-radius:12px;overflow:hidden">
        <div style="aspect-ratio:16/9;background:#f2f3f5"><img src="${img}" alt="${x.tytul||""}" style="width:100%;height:100%;object-fit:cover"></div>
        <div style="padding:12px">
          <h3 style="margin:0 0 8px;font-size:18px;color:#111">${x.tytul||"Ogłoszenie"}</h3>
          <p style="margin:0 0 6px;color:#56616c;font-size:13px">${x.lokalizacja||""}</p>
          <p style="margin:0 0 8px;font-weight:700">${money(x.cena, x.waluta||"PLN")}</p>
          ${cechy?`<p style="margin:0;color:#56616c;font-size:12px">${cechy}</p>`:""}
        </div>
      </article>
    `);
  });
}

/* ——— Główna podmiana w obrębie SEKCJI ——— */
async function replaceInSection(){
  // usuń stare artefakty (nasze) gdziekolwiek, żeby zniknęło „0 busów” w złym miejscu
  document.querySelectorAll(".supabase-count-badge,#supabase-feed-root").forEach(n=>n.remove());

  const ctx = findListingSection();
  if(!ctx) return;
  const { section, heading } = ctx;

  // utwórz własny root pod listę zaraz pod nagłówkiem
  let root = section.querySelector("#supabase-feed-root");
  if(!root){
    root = document.createElement("div");
    root.id = "supabase-feed-root";
    root.style.marginTop = "12px";
    heading.after(root);
  }

  // ukryj mockowy grid TYLKO w tej sekcji
  const mock = findMockGrid(section);
  if(mock){ mock.style.display = "none"; mock.setAttribute("data-hidden-by-supabase","true"); }

  // pobierz dane i wyrenderuj
  const data = await fetchListings();
  const count = Array.isArray(data) ? data.length : 0;

  const badge = ensureCounter(heading);
  badge.textContent = pluralizeBus(count);

  root.innerHTML = "";
  if(count){
    const grid = el(`<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px"></div>`);
    renderCards(data).forEach(card=>grid.appendChild(card));
    root.appendChild(grid);
  }else{
    root.appendChild(el(`<div style="display:inline-block;padding:16px 20px;border-radius:12px;background:#0f1217;color:#cbd5e1;border:1px dashed #30363d">Brak ogłoszeń w bazie Supabase.</div>`));
  }
}

/* ——— SPA: odśwież po każdej zmianie trasy / załadowaniu ——— */
function onRoute(){
  const p = location.pathname;
  if (p === "/" || /^\/ogloszenia(\/|$)/.test(p)) {
    setTimeout(replaceInSection, 50);
    const obs = new MutationObserver((m,o)=>{
      const hit = findListingSection();
      if(hit){ replaceInSection(); o.disconnect(); }
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
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", onRoute); else onRoute();
})();
