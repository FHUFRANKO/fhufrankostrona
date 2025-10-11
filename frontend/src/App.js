import React from 'react';
import AdsGrid from './components/AdsGrid';
import AdDetails from './components/AdDetails';

let Original = null;
try { Original = require('./AppOriginal').default; } catch(e) {}

export default function App() {
  const path = typeof window !== 'undefined' ? window.location.pathname : '/';
  if (path === '/' || path.startsWith('/ogloszenia')) return <AdsGrid />;
  if (path.startsWith('/ogloszenie/')) return <AdDetails />;
  return Original ? <Original /> : <AdsGrid />;
}
