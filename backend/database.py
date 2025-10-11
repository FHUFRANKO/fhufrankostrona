import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _ensure_ssl(url: str | None) -> str | None:
    if not url:
        return url
    p = urlparse(url)
    host = (p.hostname or "").lower()
    qs = dict(parse_qsl(p.query, keep_blank_values=True))
    # Supabase Postgres wymaga SSL — dopnij, jeśli brak
    if ("supabase.co" in host or "supabase.net" in host) and "sslmode" not in qs:
        qs["sslmode"] = "require"
    return urlunparse(p._replace(query=urlencode(qs)))

# Preferuj DATABASE_URL (Railway), ewentualnie SUPABASE_DB_URL
db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
db_url = _ensure_ssl(db_url)

connect_args = {}
if not db_url:
    # Fallback (dev/local): SQLite na dysku kontenera
    DEFAULT_SQLITE_PATH = "/app/data/app.db"
    Path("/app/data").mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
