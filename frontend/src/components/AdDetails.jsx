import React from 'react';
import { fetchAd } from '../api/ads';

export default function AdDetails() {
  const id = typeof window !== 'undefined' ? Number(window.location.pathname.split('/').pop()) : null;
  const [ad, setAd] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!id) return;
    let alive = true;
    fetchAd(id).then(d => { if (alive) { setAd(d); setError(null); }}).catch(e => setError(String(e))).finally(()=> setLoading(false));
    return () => { alive = false; }
  }, [id]);

  if (!id) return <div style={{padding:24}}>Nieprawidłowy adres URL.</div>;
  if (loading) return <div style={{padding:24}}>Ładowanie…</div>;
  if (error) return <div style={{padding:24, color:'#b00020'}}>Błąd: {error}</div>;
  if (!ad) return <div style={{padding:24}}>Nie znaleziono ogłoszenia.</div>;

  return (
    <div style={{maxWidth:1000, margin:'0 auto', padding:16}}>
      <h1 style={{marginBottom:8}}>{ad.title}</h1>
      {ad.image_url && <img src={ad.image_url} alt={ad.title} style={{width:'100%', borderRadius:12, margin:'12px 0'}}/>}
      <div style={{fontSize:18, margin:'8px 0'}}><strong>Cena:</strong> {typeof ad.price === 'number' ? ad.price.toLocaleString('pl-PL', { style:'currency', currency:'PLN' }) : '—'}</div>
      <div style={{margin:'8px 0'}}><strong>Miasto:</strong> {ad.city ?? '—'}</div>
      <p style={{whiteSpace:'pre-wrap'}}>{ad.description ?? '—'}</p>
      <div style={{marginTop:16}}><a href="/ogloszenia">← Powrót do listy</a></div>
    </div>
  );
}
