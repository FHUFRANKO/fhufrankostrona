import express from "express";
import path from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 3000;
const STATIC_DIR = path.join(__dirname, "bowdowa");
// === INSERT: SSR Ogłoszenia (above static) ===
function h(s){return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function money(v, wal="PLN"){ if(v==null) return ""; try{ return new Intl.NumberFormat("pl-PL",{style:"currency",currency:wal}).format(Number(v)); }catch{ return v+" "+wal; } }
function card(x){
  const img = (Array.isArray(x.zdjecia) && x.zdjecia[0]) ? x.zdjecia[0] : "https://placehold.co/640x360?text=Brak+zdjecia";
  const cechy = (Array.isArray(x.cechy)?x.cechy:[]).slice(0,6).map(h).join(" · ");
  return `<article class="card">
    <img src="${h(img)}" alt="${h(x.tytul||"")}" class="thumb"/>
    <div class="body">
      <h3>${h(x.tytul||"Ogłoszenie")}</h3>
      <p class="meta">${h(x.lokalizacja||"")}</p>
      <p class="price">${money(x.cena, x.waluta||"PLN")}</p>
      ${cechy?`<p class="tags">${cechy}</p>`:""}
    </div></article>`;
}
function render(list){
  const items = Array.isArray(list)?list:[];
  return `<!doctype html><html lang="pl"><head>
  <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Ogłoszenia</title>
  <style>
    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;margin:0;background:#0b0c0e;color:#e7eaee}
    header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid #1f232a}
    .wrap{max-width:1200px;margin:0 auto;padding:24px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
    .card{background:#13161b;border:1px solid #1f232a;border-radius:12px;overflow:hidden}
    .thumb{width:100%;aspect-ratio:16/9;object-fit:cover;background:#0e1116}
    .body{padding:12px}
    .meta{color:#9aa4b2;font-size:13px;margin:0 0 6px}
    .price{font-weight:700;margin:0 0 8px}
    .tags{color:#9aa4b2;font-size:12px}
    .empty{padding:48px;text-align:center;color:#9aa4b2;border:1px dashed #30363d;border-radius:12px;background:#0f1217}
  </style></head><body>
    <header><div><a href="/">← Powrót</a></div><strong>Ogłoszenia</strong><div></div></header>
    <main class="wrap">${items.length?`<div class="grid">${items.map(card).join("")}</div>`:`<div class="empty">Brak ogłoszeń w bazie Supabase.</div>`}</main>
  </body></html>`;
}
async function fetchListings(supabase, table){
  const { data, error } = await supabase.from(table).select("*").order("created_at",{ascending:false});
  if(error){ console.error("Supabase:", error.message); return []; }
  return data||[];
}
app.get(/^/ogloszenia/?$/, async (_req, res) => {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || "";
  const table = process.env.SUPABASE_TABLE || "ogloszenia";
  if(!supabaseUrl || !supabaseKey){ return res.status(500).send("Brak konfiguracji Supabase"); }
  const supabase = createClient(supabaseUrl, supabaseKey);
  const items = await fetchListings(supabase, table);
  res.set("Content-Type","text/html; charset=utf-8").send(render(items));
});
// === /INSERT: SSR Ogłoszenia (above static) ===
app.use(express.static(STATIC_DIR));
app.get("*", (_, res) => res.sendFile(path.join(STATIC_DIR, "index.html")));
app.listen(PORT, "0.0.0.0", () => console.log("Serving", STATIC_DIR, "on", PORT));

/* ===== Supabase API for listings ===== */
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const supabase = (supabaseUrl && supabaseKey) ? createClient(supabaseUrl, supabaseKey) : null;
const SUPABASE_TABLE = process.env.SUPABASE_TABLE || "ogloszenia";

app.get("/api/listings", async (_req, res) => {
  try {
    if (!supabase) return res.status(500).json({ error: "Supabase not configured" });
    let q = supabase.from(SUPABASE_TABLE).select("*").order("created_at", { ascending: false });
    const { data, error } = await q;
    if (error) return res.status(500).json({ error: error.message });
    res.json(data || []);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});
/* ===== /Supabase API ===== */
