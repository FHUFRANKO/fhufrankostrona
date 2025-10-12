import os, re, socket
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _sanitize_host_brackets(url: str) -> str:
    if not url:
        return url
    m = re.match(r'^([a-zA-Z0-9+.-]+://)([^/]+)(/.*)?$', url)
    if not m:
        return url
    scheme, netloc, rest = m.group(1), m.group(2), m.group(3) or ''
    # Usuń przypadkowe [] wokół hosta (IPv6 format nie dla domen)
    if not netloc.startswith('['):
        netloc = netloc.replace('@[', '@').replace(']@', '@').replace(']:', ':').replace('[', '').replace(']', '')
    return f"{scheme}{netloc}{rest}"

def _force_ipv4_in_netloc(p):
    """Zastąp host w p.netloc jego adresem IPv4, zachowując user:pass i port."""
    netloc = p.netloc
    creds = ''
    hostport = netloc
    if '@' in netloc:
        creds, hostport = netloc.rsplit('@', 1)
    host = hostport
    port = p.port or 5432
    if ':' in hostport:
        host, _maybe_port = hostport.rsplit(':', 1)
        # port bierzemy z p.port (pewniejsze)
    try:
        ipv4 = socket.gethostbyname(host)
    except Exception:
        return p.netloc  # nie udało się -> zostaw jak było
    new_hostport = f"{ipv4}:{port}"
    return f"{creds}@{new_hostport}" if creds else new_hostport

def _enrich_supabase(url: str) -> str:
    url = _sanitize_host_brackets(url)
    p = urlparse(url)
    qs = dict(parse_qsl(p.query, keep_blank_values=True))
    host = (p.hostname or '').lower()

    if host.endswith('supabase.co') or host.endswith('supabase.net'):
        # 1) SSL zawsze
        qs.setdefault('sslmode', 'require')
        # 2) Wymuś IPv4 – podmień host w netloc na IPv4 (żeby libpq nie wybierał IPv6)
        new_netloc = _force_ipv4_in_netloc(p)
        return urlunparse(p._replace(netloc=new_netloc, query=urlencode(qs)))

    # Nie Supabase – tylko dopnij sslmode jeżeli podano
    if 'sslmode' not in qs and p.scheme.startswith('postgres'):
        qs['sslmode'] = 'require'
    return urlunparse(p._replace(query=urlencode(qs)))

def _db_url():
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if url:
        url = _enrich_supabase(url)
    if not url:
        Path("/app/data").mkdir(parents=True, exist_ok=True)
        return "sqlite:////app/data/app.db", {"check_same_thread": False}
    if url.startswith("sqlite"):
        return url, {"check_same_thread": False}
    return url, {}

db_url, connect_args = _db_url()
engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
