(()=> {
  const path = () => location.pathname.toLowerCase();
  const onAds = () => path().includes("ogloszenia");
  if (!onAds()) return;

  const ENV = window.ENV || {};
  const URL = ENV.SUPABASE_URL;
  const KEY = ENV.SUPABASE_ANON_KEY;
  const TABLE = ENV.SUPABASE_TABLE || "ogloszenia";

  // Znajdź i podmień badge "XX busów"
  const findHeaderBadge = () => {
    // spróbuj znaleźć nagłówek z tekstem
    const hdr = [...document.querySelectorAll("h1,h2,h3")].find(h => (h.textContent||"").toLowerCase().includes("busy i samochody"));
    if (hdr) {
      // poszukaj w rodzeństwie czegoś co wygląda jak "XX busów"
      const sibs = [hdr, ...hdr.parentElement?.querySelectorAll("*") || []];
      const m = sibs.find(n => /\d+\s*bus(ów|y)/i.test((n.textContent||"").trim()));
      if (m) return m;
    }
    // fallback: globalnie pierwszy element z "XX bus..."
    return [...document.querySelectorAll("span,div,strong,em,button")].find(n => /\d+\s*bus(ów|y)/i.test((n.textContent||"").trim())) || null;
  };

  const updateBadge = (count) => {
    const el = findHeaderBadge();
    if (!el) return;
    el.textContent = (el.textContent||"").replace(/\d+\s*bus(ów|y)/i, `${count} busów`);
  };

  // Usuń liczby w nawiasach przy filtrach (np. "(32)")
  const stripFilterCounts = () => {
    document.querySelectorAll("button, a, span, div").forEach(n => {
      const t = (n.textContent||"").trim();
      if (/\(.+\)/.test(t) && /[0-9]/.test(t)) {
        n.textContent = t.replace(/\s*\(\s*\d+\s*\)\s*/g, " ");
      }
    });
  };

  // Schowaj paginację (zostawiamy Twoją listę z Supabase)
  const hidePagination = () => {
    const cand = [...document.querySelectorAll("nav,ul,div")].find(n => {
      const t = (n.textContent||"").toLowerCase();
      return /\bpoprzednia\b/.test(t) && /\bnastępna\b/.test(t);
    });
    if (cand) cand.style.display = "none";
  };

  // Pobierz count z Supabase (active=true)
  const fetchCount = () => {
    if (!URL || !KEY) { updateBadge(0); return; }
    const endpoint = URL.replace(/\/$/,"") + "/rest/v1/" + encodeURIComponent(TABLE) + "?active=eq.true&select=id";
    fetch(endpoint, {
      method: "GET",
      headers: { apikey: KEY, Authorization: "Bearer " + KEY, Prefer: "count=exact" },
      cache: "no-store"
    }).then(async r => {
      const cr = r.headers.get("Content-Range"); // np. "0-0/NN"
      if (cr && /\/\d+/.test(cr)) {
        const m = cr.match(/\/(\d+)/); const total = m ? parseInt(m[1],10) : 0;
        updateBadge(Number.isFinite(total) ? total : 0);
        if ((total|0) === 0) hidePagination();
        return;
      }
      const data = r.ok ? await r.json() : [];
      const total = Array.isArray(data) ? data.length : 0;
      updateBadge(total);
      if (total === 0) hidePagination();
    }).catch(() => { updateBadge(0); hidePagination(); });
  };

  const refresh = () => { stripFilterCounts(); fetchCount(); };

  // Start + reaguj na zmiany SPA
  const boot = () => {
    if (!onAds()) return;
    refresh();
  };

  if (document.readyState === "complete" || document.readyState === "interactive") {
    setTimeout(boot, 50);
  } else {
    document.addEventListener("DOMContentLoaded", () => setTimeout(boot, 50), { once:true });
  }

  let tm;
  const mo = new MutationObserver(() => {
    if (!onAds()) return;
    clearTimeout(tm);
    tm = setTimeout(refresh, 120); // debounce
  });
  mo.observe(document.documentElement, { childList:true, subtree:true });
})();
