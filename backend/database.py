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
    # Usuń przypadkowe [] jeśli to nie jest IPv6 literal
    if not netloc.startswith('['):
        netloc = netloc.replace('@[', '@').replace(']@', '@').replace(']:', ':').replace('[', '').replace(']', '')
    return f"{scheme}{netloc}{rest}"

def _ensure_ssl_and_timeout(url: str) -> str:
    p = urlparse(url)
    qs = dict(parse_qsl(p.query, keep_blank_values=True))
    # sslmode + niski timeout połączenia
    qs.setdefault('sslmode', 'require')
    qs.setdefault('connect_timeout', '5')
    return urlunparse(p._replace(query=urlencode(qs)))

def _db_url_and_args():
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not url:
        Path("/app/data").mkdir(parents=True, exist_ok=True)
        return "sqlite:////app/data/app.db", {"check_same_thread": False}

    url = _sanitize_host_brackets(url)
    url = _ensure_ssl_and_timeout(url)

    p = urlparse(url)
    hostname = (p.hostname or '').lower()
    connect_args = {}

    # Jeśli Supabase i port 5432 — rozwiąż na IPv4 i daj go jako hostaddr (libpq)
    if hostname.endswith('supabase.co') or hostname.endswith('supabase.net'):
        try:
            ipv4 = socket.getaddrinfo(hostname, p.port or 5432, family=socket.AF_INET)[0][4][0]
            # przekazuj hostaddr via connect_args — działa pewniej z SQLAlchemy+psycopg2
            connect_args['hostaddr'] = ipv4
        except Exception:
            pass

    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    return url, connect_args

db_url, connect_args = _db_url_and_args()
engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
