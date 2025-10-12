async function fetchListings(){
  try{
    const r = await fetch("/api/listings",{cache:"no-store"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }catch(e){ console.error("Listings fetch error:", e); return []; }
}
function money(v, wal="PLN"){ if(v==null) return ""; try{ return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); } catch { return `${v} ${wal}`; } }
function el(html){ const t=document.createElement("template"); t.innerHTML=html.trim(); return t.content.firstElementChild; }

/* Znajdź kontener kart (heurystyki) */
function findGrid(ctx=document){
  // 1) gdy istnieje sekcja z nagłówkiem "Busy i samochody dostawcze"
  const h = Array.from(ctx.querySelectorAll("h2,h3")).find(h=>/busy|samochody|ogłoszenia|ogloszenia/i.test(h.textContent||""));
  if(h){
    let n=h.parentElement;
    for(let i=0;i<6&&n;i++){ n=n.parentElement; if(!n)break; const cs=getComputedStyle(n); if(cs.display==="grid"||cs.display==="flex") return n; }
  }
  // 2) weź największy grid/flex w main
  const main = ctx.querySelector("main")||ctx;
  const grids = Array.from(main.querySelectorAll("section,div,ul"))
    .filter(x=>["grid","flex"].includes(getComputedStyle(x).display));
  return grids.sort((a,b)=>b.clientWidth*b.clientHeight - a.clientWidth*a.clientHeight)[0]||null;
}

/* Wygeneruj prostą kartę (neutralne style, nie psują layoutu) */
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

async function replaceOnPage(ctx=document){
  const data = await fetchListings();
  const grid = findGrid(ctx);
  if(!grid) return;

  // ukryj stare mocki
  grid.setAttribute("data-static-cards","true");
  while(grid.firstChild) grid.removeChild(grid.firstChild);

  // wstaw nowe
  if(Array.isArray(data) && data.length){
    renderCards(data).forEach(card=>grid.appendChild(card));
  }else{
    grid.appendChild(el(`<div style="padding:24px;border:1px dashed #30363d;border-radius:12px;color:#9aa4b2;background:#0f1217">Brak ogłoszeń w bazie Supabase.</div>`));
  }
}

(async ()=>{
  // działa na stronie głównej i na /ogloszenia – ten sam skrypt
  await replaceOnPage(document);
})();
