// Environment configuration
window.ENV = window.ENV || {};
Object.assign(window.ENV, {
  SUPABASE_URL: "${SUPABASE_URL}",
  SUPABASE_ANON_KEY: "${SUPABASE_ANON_KEY}",
  API_BASE_URL: "${API_BASE_URL}"
});
