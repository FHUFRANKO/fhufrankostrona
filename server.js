import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { createClient } from "@supabase/supabase-js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const PORT = process.env.PORT || 3000;
const STATIC_DIR = path.join(__dirname, "bowdowa");

app.use(express.json({ limit: "5mb" }));

// Supabase
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || "";
const TABLE = process.env.SUPABASE_TABLE || "ogloszenia";
const ADMIN_CODE = process.env.ADMIN_CODE || "";
const supabase = (supabaseUrl && supabaseKey) ? createClient(supabaseUrl, supabaseKey) : null;

const ensureSupabase = (res) => {
  if (!supabase) { res.status(500).json({ error: "Supabase not configured" }); return false; }
  return true;
};
const requireAdmin = (req, res) => {
  if (!ADMIN_CODE || req.headers["x-admin-code"] !== ADMIN_CODE) {
    res.status(401).json({ error: "Unauthorized" }); return false;
  }
  return true;
};

async function fetchListings() {
  if (!supabase) return [];
  const { data, error } = await supabase.from(TABLE).select("*").order("created_at", { ascending: false });
  if (error) { console.error("Supabase:", error.message); return []; }
  return data || [];
}

/* API */
app.get("/api/listings", async (_req, res) => {
  if (!ensureSupabase(res)) return;
  res.json(await fetchListings());
});
app.post("/api/listings", async (req, res) => {
  if (!ensureSupabase(res)) return;
  if (!requireAdmin(req, res)) return;
  const { data, error } = await supabase.from(TABLE).insert(req.body).select();
  if (error) return res.status(400).json({ error: error.message });
  res.status(201).json(data);
});
app.patch("/api/listings/:id", async (req, res) => {
  if (!ensureSupabase(res)) return;
  if (!requireAdmin(req, res)) return;
  const { id } = req.params;
  const { data, error } = await supabase.from(TABLE).update(req.body).eq("id", id).select();
  if (error) return res.status(400).json({ error: error.message });
  res.json(data);
});
app.delete("/api/listings/:id", async (req, res) => {
  if (!ensureSupabase(res)) return;
  if (!requireAdmin(req, res)) return;
  const { id } = req.params;
  const { error } = await supabase.from(TABLE).delete().eq("id", id);
  if (error) return res.status(400).json({ error: error.message });
  res.status(204).end();
});

/* Przechwycenie typowych mock-JSON -> zwracaj prawdziwe dane */
app.get(/^\/(data|mock|mocks)\/.*\.json$/i, async (_req, res) => {
  if (!ensureSupabase(res)) return;
  res.json(await fetchListings());
});

/* Statyczne pliki + SPA fallback */
app.use(express.static(STATIC_DIR));
app.get("*", (_req, res) => res.sendFile(path.join(STATIC_DIR, "index.html")));

app.listen(PORT, "0.0.0.0", () => console.log(`Serving ${STATIC_DIR} on ${PORT}`));
