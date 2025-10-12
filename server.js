import express from "express";
import path from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 3000;
const STATIC_DIR = path.join(__dirname, "bowdowa");
app.use(express.static(STATIC_DIR));
app.get("*", (_, res) => res.sendFile(path.join(STATIC_DIR, "index.html")));
app.listen(PORT, "0.0.0.0", () => console.log("Serving", STATIC_DIR, "on", PORT));

/* ===== Supabase API for listings ===== */
import { createClient } from "@supabase/supabase-js";
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
