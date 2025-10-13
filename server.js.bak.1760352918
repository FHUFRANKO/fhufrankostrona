import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// ----- Supabase API -----
const SUPABASE_URL  = process.env.SUPABASE_URL;
const SUPABASE_KEY  = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const SUPABASE_TABLE = process.env.SUPABASE_TABLE || "ogloszenia";

let supabase = null;
if (SUPABASE_URL && SUPABASE_KEY) {
  supabase = createClient(SUPABASE_URL, SUPABASE_KEY, { auth: { persistSession: false } });
}

app.get("/api/healthz", (_req, res) => res.json({ ok:true }));
app.get("/api/listings", async (_req, res) => {
  try {
    if (!supabase) return res.json([]);
    const { data, error } = await supabase.from(SUPABASE_TABLE).select("*").order("created_at", { ascending:false }).limit(60);
    if (error) return res.status(500).json({ error: error.message });
    return res.json(data || []);
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
});

// ----- Statyczny frontend + fallback SPA -----
const candidates = [
  path.join(__dirname, "frontend"),
  path.join(__dirname, "public"),
  path.join(__dirname, "dist"),
  path.join(__dirname, "build"),
  path.join(__dirname, ".")
];
const staticRoot = candidates.find(p => {
  try { return require("fs").existsSync(path.join(p, "index.html")); } catch { return false; }
}) || candidates[0];

app.use(express.static(staticRoot, { extensions: ["html"] }));

// Fallback – tylko dla GET i nie-API
app.get("*", (req, res, next) => {
  if (req.path.startsWith("/api/")) return next();
  const indexPath = path.join(staticRoot, "index.html");
  res.sendFile(indexPath, err => {
    if (err) next(); // jeśli nie ma index.html, niech Express zwróci 404
  });
});

// Start
app.listen(PORT, () => {
  console.log(`✅ Server running on port ${PORT}. Static root: ${staticRoot}`);
});
