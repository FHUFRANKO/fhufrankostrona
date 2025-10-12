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
    # Usuń przypadkowe [] jeśli to nie jest literal IPv6
    if not netloc.startswith('['):
        netloc = netloc.replace('@[', '@').replace(']@', '@').replace(']:', ':').replace('[', '').replace(']', '')
    return f"{scheme}{netloc}{rest}"

def _force_ipv4_netloc(p):
    """Podmień host w p.netloc na IPv4 (zachowaj user:pass i port)."""
    netloc = p.netloc
    creds = ''
    hostport = netloc
    if '@' in netloc:
        creds, hostport = netloc.rsplit('@', 1)
    host = hostport
    port = p.port or 5432
    if ':' in hostport:
        host, _maybe_port = hostport.rsplit(':', 1)
    try:
        ipv4 = socket.gethostbyname(host)
    except Exception:
        return p.netloc
    new_hostport = f"{ipv4}:{port}"
    return f"{creds}@{new_hostport}" if creds else new_hostport

def _enrich(url: str) -> str:
    url = _sanitize_host_brackets(url)
    p = urlparse(url)
    qs = dict(parse_qsl(p.query, keep_blank_values=True))

    # ssl + rozsądny timeout
    qs.setdefault('sslmode', 'require')
    qs.setdefault('connect_timeout', '5')

    host = (p.hostname or '').lower()
    port = p.port or 5432

    # Jeśli Supabase – wymuś IPv4 oraz, jeśli ktoś podał 5432, użyj 6543 (Pooler)
    if host.endswith('supabase.co') or host.endswith('supabase.net'):
        # IPv4
        new_netloc = _force_ipv4_netloc(p)

        # port 6543 (Pooler) – stabilniej w PaaSach
        if port == 5432:
            # nadpisz port w netloc
            if ':' in new_netloc:
                left, _ = new_netloc.rsplit(':', 1)
                new_netloc = f"{left}:6543"
            else:
                new_netloc = f"{new_netloc}:6543"

        return urlunparse(p._replace(netloc=new_netloc, query=urlencode(qs)))

    return urlunparse(p._replace(query=urlencode(qs)))

def _db_url_and_args():
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not url:
        Path("/app/data").mkdir(parents=True, exist_ok=True)
        return "sqlite:////app/data/app.db", {"check_same_thread": False}
    url = _enrich(url)
    if url.startswith("sqlite"):
        return url, {"check_same_thread": False}
    return url, {}

db_url, connect_args = _db_url_and_args()
engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
