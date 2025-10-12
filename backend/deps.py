from fastapi import Depends, Header, HTTPException, status
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_required(x_admin_token: str | None = Header(None, alias="X-Admin-Token")):
    import os
    expected = os.getenv("ADMIN_TOKEN")
    if not expected:
        return
    if x_admin_token != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
