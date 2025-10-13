(()=> {
  const ENV = window.ENV || {};
  const URL = ENV.SUPABASE_URL;
  const KEY = ENV.SUPABASE_ANON_KEY;
  const TABLE = ENV.SUPABASE_TABLE || "ogloszenia";
  if (!URL || !KEY) return;

  // znajdź w DOM element z napisem "XX busów"
  const findCounter = () => {
    const nodes = document.querySelectorAll("h1,h2,h3,div,span,strong,em");
    for (const n of nodes) {
      const t = (n.textContent || "").toLowerCase().trim();
      if (/\d+\s*bus(ów|y|ów?)/.test(t)) return n;
    }
    return null;
  };

  const updateCounter = (count) => {
    const el = findCounter();
    if (!el) return;
    // podmień tylko liczbę, resztę zostaw
    const txt = el.textContent;
    const repl = String(txt).replace(/\d+\s*bus(ów|y|ów?)/i, `${count} busów`);
    el.textContent = repl;
  };

  const fetchCount = () => {
    const endpoint = URL.replace(/\/$/, "") + "/rest/v1/" + encodeURIComponent(TABLE) + "?active=eq.true&select=id";
    fetch(endpoint, {
      method: "GET",
      headers: {
        apikey: KEY,
        Authorization: "Bearer " + KEY,
        Prefer: "count=exact",   // PostgREST zwróci liczbę w Content-Range
      },
      cache: "no-store"
    }).then(async (r) => {
      // próba odczytu z nagłówka Content-Range: "0-0/NN"
      const cr = r.headers.get("Content-Range");
      if (cr && /\/\d+/.test(cr)) {
        const m = cr.match(/\/(\d+)/);
        const total = m ? parseInt(m[1], 10) : 0;
        updateCounter(Number.isFinite(total) ? total : 0);
        return;
      }
      // fallback: zlicz z JSON-a
      const data = r.ok ? await r.json() : [];
      updateCounter(Array.isArray(data) ? data.length : 0);
    }).catch(() => updateCounter(0));
  };

  const init = () => {
    // odśwież licznik tylko na stronach głównej i /ogloszenia
    const path = location.pathname.toLowerCase();
    if (path === "/" || path.includes("ogloszenia")) fetchCount();
  };

  if (document.readyState === "complete" || document.readyState === "interactive") {
    setTimeout(init, 50);
  } else {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  }

  // reaguj na zmiany w SPA
  const mo = new MutationObserver(() => {
    const path = location.pathname.toLowerCase();
    if (path === "/" || path.includes("ogloszenia")) fetchCount();
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
