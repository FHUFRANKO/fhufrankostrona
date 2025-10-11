export type Ad = {
  id: number;
  title: string;
  description?: string;
  price?: number;
  city?: string;
  image_url?: string;
  is_active?: boolean;
};

const API = (process.env.REACT_APP_API_URL || '/api').replace(/\/+$/,'');

export async function fetchAds(start = 0, end = 23): Promise<Ad[]> {
  const qs = new URLSearchParams({
    filter: JSON.stringify({ is_active: true }),
    sort: JSON.stringify(['created_at','DESC']),
    range: JSON.stringify([start,end]),
  }).toString();
  const res = await fetch(`${API}/ads?${qs}`, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchAd(id: number): Promise<Ad> {
  const res = await fetch(`${API}/ads/${id}`, { headers: { 'Accept': 'application/json' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
