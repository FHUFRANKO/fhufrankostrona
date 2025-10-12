// Dynamic replacement of mock cards on homepage
async function fetchListings(){
  try{
    const r = await fetch("/api/listings", {cache:"no-store"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }catch(e){
    console.error("Listings fetch error:", e);
    return [];
  }
}

function el(html){
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

function money(v, wal="PLN"){
  if(v==null) return "";
  try { return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); }
  catch { return `${v} ${wal}`; }
}

function findStaticGrid(){
  // szukamy typowego gridu z przyciskiem "Szczegóły"
  const buttons = Array.from(document.querySelectorAll("a,button"))
    .filter(b => /szczeg|szczegóły/i.test(b.textContent||""));
  for(const btn of buttons){
    let n = btn;
    for(let i=0;i<6 && n;i++){
      n = n.parentElement;
      if(!n) break;
      const cls = (n.className||"").toString().toLowerCase();
      if(/grid|cards|card|list|offers|oglosz|ogłosz/.test(cls)) return n;
      const cs = getComputedStyle(n);
      if(cs.display==="grid" || cs.display==="flex") return n;
    }
  }
  // fallback: największy grid na stronie
  const grids = Array.from(document.querySelectorAll("main,section,div"))
    .filter(x => {
      const cs = getComputedStyle(x);
      return cs.display==="grid" || cs.display==="flex";
    });
  return grids.sort((a,b)=>b.clientWidth*b.clientHeight - a.clientWidth*a.clientHeight)[0] || null;
}

function renderCards(list){
  return list.map(x=>{
    const img = Array.isArray(x.zdjecia)&&x.zdjecia[0] ? x.zdjecia[0] : "https://placehold.co/640x360?text=Brak+zdjecia";
    const cechy = Array.isArray(x.cechy) ? x.cechy.slice(0,6).join(" • ") : "";
    return el(`
      <article class="vis-dyn-card" style="background:#13161b;border:1px solid #1f232a;border-radius:12px;overflow:hidden">
        <div style="aspect-ratio:16/9;background:#0e1116">
          <img src="${img}" alt="${x.tytul||""}" style="width:100%;height:100%;object-fit:cover">
        </div>
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

(async ()=>{
  const list = await fetchListings();

  // znajdź istniejący grid i go ukryj (mock)
  const staticGrid = findStaticGrid();
  if(staticGrid){
    staticGrid.setAttribute("data-static-cards","true");
    staticGrid.style.display = "none";
  }

  // utwórz dynamiczny grid
  const holder = document.getElementById("dynamic-listings-root") || (()=> {
    const h = document.createElement("section");
    h.id = "dynamic-listings-root";
    const main = document.querySelector("main") || document.body;
    main.insertBefore(h, main.firstChild);
    return h;
  })();

  holder.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin:16px 0">
      <h2 style="margin:0;color:#fff;font-size:22px">Aktualne ogłoszenia</h2>
      <a href="/ogloszenia" style="color:#ffd166;text-decoration:none">Zobacz wszystkie →</a>
    </div>
    <div class="vis-dyn-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px"></div>
  `;

  const grid = holder.querySelector(".vis-dyn-grid");
  if(Array.isArray(list) && list.length){
    renderCards(list).forEach(card=>grid.appendChild(card));
  }else{
    grid.replaceWith(el(`<div style="padding:24px;border:1px dashed #30363d;border-radius:12px;color:#9aa4b2;background:#0f1217">
      Brak ogłoszeń w bazie Supabase.
    </div>`));
  }
})();
