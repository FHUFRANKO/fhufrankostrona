import React from 'react';
import { fetchAds } from '../api/ads';

export default function AdsGrid() {
  const [ads, setAds] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchAds({ start: 0, end: 23 })
      .then((data) => { if (alive) { setAds(data); setError(null); } })
      .catch((e) => { if (alive) setError(String(e)); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, []);

  if (loading) return <div style={{padding:24}}>Ładowanie ogłoszeń…</div>;
  if (error) return <div style={{padding:24, color:'#b00020'}}>Błąd: {error}</div>;
  if (!ads.length) return <div style={{padding:24}}>Brak ogłoszeń.</div>;

  return (
    <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:16, padding:16}}>
      {ads.map(ad => (
        <article key={ad.id} style={{border:'1px solid #eee', borderRadius:12, overflow:'hidden', boxShadow:'0 2px 8px rgba(0,0,0,0.06)'}}>
          <div style={{position:'relative', paddingTop:'62%'}}>
            {ad.image_url ? (
              <img src={ad.image_url} alt={ad.title} style={{position:'absolute', inset:0, width:'100%', height:'100%', objectFit:'cover'}} />
            ) : (
              <div style={{position:'absolute', inset:0, display:'grid', placeItems:'center', background:'#f6f6f6'}}>Brak zdjęcia</div>
            )}
          </div>
          <div style={{padding:'12px 14px'}}>
            <h3 style={{margin:'0 0 6px', fontSize:18, lineHeight:1.2}}>{ad.title}</h3>
            <div style={{fontSize:14, color:'#555', marginBottom:8}}>{ad.city ?? '—'}</div>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <strong style={{fontSize:18}}>
                {typeof ad.price === 'number' ? ad.price.toLocaleString('pl-PL', { style:'currency', currency:'PLN' }) : '—'}
              </strong>
              <a href={`/ogloszenie/${ad.id}`} style={{textDecoration:'none', fontSize:14}}>Szczegóły →</a>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
