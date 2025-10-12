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
    # Jeśli to nie jest IPv6 w [] – usuń nawiasy, które czasem lądują w ENV
    if not netloc.startswith('['):
        netloc = netloc.replace('@[', '@').replace(']@', '@').replace(']:', ':').replace('[', '').replace(']', '')
    return f"{scheme}{netloc}{rest}"

def _enrich_supabase(url: str) -> str:
    url = _sanitize_host_brackets(url)
    p = urlparse(url)
    qs = dict(parse_qsl(p.query, keep_blank_values=True))
    host = (p.hostname or '').lower()
    port = p.port or 5432

    if host.endswith('supabase.co') or host.endswith('supabase.net'):
        # 1) SSL zawsze włączone
        qs.setdefault('sslmode', 'require')
        # 2) Jeśli środowisko nie ma IPv6 – dołącz IPv4 przez hostaddr (libpq)
        try:
            info = socket.getaddrinfo(host, port, family=socket.AF_INET)
            if info:
                ipv4 = info[0][4][0]
                qs['hostaddr'] = ipv4
        except Exception:
            # brak IPv4? – zostaw jak jest, libpq spróbuje po kolei
            pass

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
