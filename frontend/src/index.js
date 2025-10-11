import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import AdsGrid from './live/AdsGrid';
import AdDetails from './live/AdDetails';

const root = createRoot(document.getElementById('root'));
const path = window.location.pathname;
const isList = path === '/' || path.startsWith('/ogloszenia');
const isDetails = /^\/ogloszenie\/\d+\/?$/.test(path);

root.render(
  <React.StrictMode>
    {isDetails ? <AdDetails /> : isList ? <AdsGrid /> : <App />}
  </React.StrictMode>
);
