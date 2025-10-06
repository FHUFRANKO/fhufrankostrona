import axios from "axios";
// Na Netlify mamy proxy /api -> backend na Railway
// Lokalne dev: patrz setupProxy.js (proxy /api -> http://localhost:8000)
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE || "/api",
  headers: { "Content-Type": "application/json" },
});
export default api;
