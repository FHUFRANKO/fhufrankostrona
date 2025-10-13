import express from "express";
import cors from "cors";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const app  = express();
const PORT = process.env.PORT || 8080;

app.use(cors());
app.use(express.json());

// ---------- Supabase ----------
const SUPABASE_URL   = process.env.SUPABASE_URL;
const SUPABASE_KEY   = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const SUPABASE_TABLE = process.env.SUPABASE_TABLE || "ogloszenia";
let supabase = (SUPABASE_URL && SUPABASE_KEY) ? createClient(SUPABASE_URL, SUPABASE_KEY, { auth: { persistSession:false } }) : null;

app.get("/api/healthz", (_req,res)=>res.json({ok:true}));
app.get("/api/listings", async (_req,res)=>{
  try{
    if(!supabase) return res.json([]);
    const { data, error } = await supabase.from(SUPABASE_TABLE).select("*").order("created_at",{ascending:false}).limit(60);
    if(error) return res.status(500).json({error:error.message});
    return res.json(data||[]);
  }catch(e){ return res.status(500).json({error:String(e)}); }
});

// ---------- Auto-detekcja frontendu ----------
const preferred = [
  "frontend/index.html","frontend/public/index.html",
  "public/index.html","dist/index.html","build/index.html","index.html"
];

function findIndexHtml() {
  for (const rel of preferred) {
    const abs = path.join(__dirname, rel);
    if (fs.existsSync(abs)) return abs;
  }
  // pełne szukanie do 3 poziomów
  const maxDepth = 3;
  const q = [[__dirname,0]];
  while(q.length){
    const [dir,depth] = q.shift();
    if (depth>maxDepth) continue;
    let entries=[];
    try{ entries = fs.readdirSync(dir,{withFileTypes:true}); }catch{ continue; }
    for(const e of entries){
      const p = path.join(dir,e.name);
      if(e.isFile() && e.name.toLowerCase()==="index.html") return p;
      if(e.isDirectory()) q.push([p,depth+1]);
    }
  }
  // fallback: pierwszy *.html jaki znajdziemy
  const qq = [[__dirname,0]];
  while(qq.length){
    const [dir,depth] = qq.shift();
    if (depth>maxDepth) continue;
    let entries=[];
    try{ entries = fs.readdirSync(dir,{withFileTypes:true}); }catch{ continue; }
    for(const e of entries){
      const p = path.join(dir,e.name);
      if(e.isFile() && /\.html?$/i.test(e.name)) return p;
      if(e.isDirectory()) qq.push([p,depth+1]);
    }
  }
  return null;
}

const INDEX_FILE = findIndexHtml();
if(!INDEX_FILE){
  console.error("❌ Nie znaleziono index.html w projekcie.");
}else{
  console.log("✅ Index file:", INDEX_FILE);
}

const staticRoot = INDEX_FILE ? path.dirname(INDEX_FILE) : __dirname;
console.log("✅ Static root:", staticRoot);

// serwowanie plików statycznych
app.use(express.static(staticRoot, { extensions:["html"] }));

// Fallback SPA (dla GET i nie-API)
app.get("*", (req,res,next)=>{
  if(req.path.startsWith("/api/")) return next();
  if(INDEX_FILE && fs.existsSync(INDEX_FILE)){
    return res.sendFile(INDEX_FILE);
  }
  return res.status(404).send("Not Found");
});

app.listen(PORT, ()=>console.log(`🚀 Server on ${PORT}`));
