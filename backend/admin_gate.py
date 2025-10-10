import os, time, jwt
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "")
ADMIN_LINK_KEY   = os.getenv("ADMIN_LINK_KEY", "")
ADMIN_CODE       = os.getenv("ADMIN_CODE", "")
ALGO = "HS256"
COOKIE = "admin_session"
COOKIE_MAX_AGE = 60*60*24*30  # 30 dni

def _encode(sub: str, ttl: int = COOKIE_MAX_AGE) -> str:
    now = int(time.time())
    return jwt.encode({"sub": sub, "iat": now, "exp": now+ttl}, ADMIN_JWT_SECRET, algorithm=ALGO)

def _decode(token: str) -> dict:
    return jwt.decode(token, ADMIN_JWT_SECRET, algorithms=[ALGO])

def gate_page(key: Optional[str]) -> HTMLResponse:
    html = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Panel Admina — bramka</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;display:flex;align-items:center;justify-content:center;height:100vh;background:#fafafa;margin:0}
.card{background:#fff;padding:24px 28px;border-radius:14px;box-shadow:0 10px 35px rgba(0,0,0,.08);max-width:380px;width:100%}
h1{font-size:18px;margin:0 0 12px}
input{width:100%;padding:12px 14px;border:1px solid #ddd;border-radius:10px;font-size:16px;outline:none}
button{margin-top:12px;width:100%;padding:12px 14px;border:0;border-radius:10px;background:#f0b400;font-weight:600;font-size:16px;cursor:pointer}
small{color:#666}
</style>
</head><body>
<div class="card">
<h1>Wpisz kod dostępu</h1>
<form id="f">
<input name="code" placeholder="Kod" autocomplete="one-time-code" required />
<input type="hidden" name="key" id="kField" />
<button>Potwierdź</button>
<small>Masz dedykowany link i kod. Nie udostępniaj dalej.</small>
</form>
<script>
const q=new URLSearchParams(location.search);
document.getElementById('kField').value = q.get('key') || '';
document.getElementById('f').addEventListener('submit', async(e)=>{
  e.preventDefault();
  const fd=new FormData(e.target);
  const r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:fd.get('code'),key:fd.get('key')})});
  if(r.ok) location.href='/admin'; else alert('Niepoprawny kod lub link.');
});
</script>
</div>
</body></html>"""
    return HTMLResponse(html)

async def login_api(payload: dict):
    key = (payload or {}).get("key") or ""
    code = (payload or {}).get("code") or ""
    if not ADMIN_JWT_SECRET or not ADMIN_LINK_KEY or not ADMIN_CODE:
        return JSONResponse({"error":"Server not configured"}, status_code=500)
    if key != ADMIN_LINK_KEY or code != ADMIN_CODE:
        return JSONResponse({"ok":False}, status_code=401)
    token = _encode(sub="admin")
    resp = JSONResponse({"ok": True})
    resp.set_cookie(COOKIE, token, httponly=True, secure=True, samesite="Strict", max_age=COOKIE_MAX_AGE, path="/")
    return resp

async def require_admin(request: Request):
    tok = request.cookies.get(COOKIE)
    if tok:
        try:
            _decode(tok); return True
        except Exception:
            pass
    # brak sesji -> jeśli jest key w URL, pokaż bramkę; inaczej przekieruj na /admin-gate
    key = request.query_params.get("key")
    if key:
        return gate_page(key)
    return RedirectResponse("/admin-gate", status_code=307)
