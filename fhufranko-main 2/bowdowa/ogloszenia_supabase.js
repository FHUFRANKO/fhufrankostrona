(() => {

  const main = document.querySelector('main') || document.body;
  // twarde wyczyszczenie gridu mockowego
  main.innerHTML = '';
  const mount = document.createElement('section');
  mount.id = 'ogloszenia-root';
  main.appendChild(mount);

  const empty = 'nie ma jeszcze żadnych ogłoszeń';
  const ENV = (window.ENV || {});
  const URL = ENV.SUPABASE_URL;
  const KEY = ENV.SUPABASE_ANON_KEY;

  const render = (arr) => {
    mount.innerHTML = arr.map(it => {
      const t = it.title ?? it.tytul ?? 'Ogłoszenie';
      const d = it.description ?? it.opis ?? '';
      const p = it.price ?? it.cena ?? '';
      const img = it.image ?? it.zdjecie ?? '';
      return (
        '<article style="border:1px solid #eee;border-radius:12px;padding:12px;margin:8px 0;display:flex;gap:12px;align-items:flex-start">' +
        (img ? '<img src="'+img+'" alt="" style="width:140px;height:100px;object-fit:cover;border-radius:8px">' : '') +
        '<div><h3 style="margin:0 0 6px 0;font-size:1.05rem">'+t+'</h3>' +
        (d ? '<p style="margin:0 0 6px 0">'+d+'</p>' : '') +
        (p ? '<div style="font-weight:600">'+p+'</div>' : '') +
        '</div></article>'
      );
    }).join('');
  };

  // brak konfiguracji → pusty stan

  // pobierz tylko aktywne ogłoszenia opublikowane w panelu (tabela: ogloszenia)
  const endpoint = URL.replace(/\/$/, '') + '/rest/v1/ogloszenia?select=*,' +
                   'title,description,price,image,active,created_at&active=eq.true&order=created_at.desc';

  fetch(endpoint, {
    headers: {
      apikey: KEY,
      Authorization: 'Bearer ' + KEY,
      'Content-Type': 'application/json'
    },
    cache: 'no-store'
  })
  .then(r => r.ok ? r.json() : [])
  .then(data => {
    // dodatkowy filtr bezpieczeństwa na ewentualne makiety
    const yes = v => v === true || v === 'true';
    const real = (Array.isArray(data) ? data : []).filter(x => {
      const t = String((x.title || x.tytul || '')).toLowerCase();
      return !(yes(x.mock) || yes(x.isMock) || yes(x.fake) || yes(x.test) || t.includes('mock'));
    });
    render(real);
  })
  .catch(() => render([]));
})();
