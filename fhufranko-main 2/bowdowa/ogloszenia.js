document.addEventListener("DOMContentLoaded", async () => {
  const mount = document.getElementById("ogloszenia-root") || (() => {
    const el = document.createElement("section"); el.id = "ogloszenia-root"; document.body.appendChild(el); return el;
  })();
  const empty = "nie ma jeszcze żadnych ogłoszeń";
  try {
    const r = await fetch("ogloszenia.json",{cache:"no-store"});
    const data = r.ok ? await r.json() : [];
    const list = Array.isArray(data) ? data : (Array.isArray(data.items) ? data.items : []);
    const real = list.filter(x => {
      const yes = v => v===true || v==="true";
      const t = (x.title||x.tytul||"").toString().toLowerCase();
      return !(yes(x.mock)||yes(x.isMock)||yes(x.fake)||yes(x.test)||t.includes("mock"));
    });
    if (!real.length) { mount.textContent = empty; return; }
    mount.innerHTML = real.map(it => `
      <article style="border:1px solid #eee;border-radius:12px;padding:12px;margin:8px 0">
        <h3 style="margin:0 0 6px 0">${(it.title||it.tytul||"Ogłoszenie")}</h3>
        ${it.description||it.opis?`<p style="margin:0 0 6px 0">${(it.description||it.opis)}</p>`:""}
        ${it.price||it.cena?`<div style="font-weight:600">${(it.price||it.cena)}</div>`:""}
      </article>`).join("");
  } catch { mount.textContent = empty; }
});
