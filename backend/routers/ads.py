from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import json

from .. import models, schemas
from ..deps import get_db, admin_required

router = APIRouter(prefix="/api/ads", tags=["ads"])

def _apply_ra_params(q, request: Request):
    f = request.query_params.get("filter")
    if f:
        try:
            f = json.loads(f)
            if "q" in f and f["q"]:
                q = q.filter(models.Ad.title.ilike(f"%{f['q']}%"))
            if "is_active" in f:
                q = q.filter(models.Ad.is_active == bool(f["is_active"]))
        except Exception:
            pass

    s = request.query_params.get("sort")
    if s:
        try:
            field, order = json.loads(s)
            col = getattr(models.Ad, field, None)
            if col is not None:
                q = q.order_by(col.desc() if str(order).upper() == "DESC" else col.asc())
        except Exception:
            pass
    else:
        q = q.order_by(models.Ad.created_at.desc())

    r = request.query_params.get("range")
    start, end = 0, None
    if r:
        try:
            start, end = json.loads(r)
        except Exception:
            pass
    return q, start, end

@router.get("", response_model=List[schemas.AdOut])
def list_ads(request: Request, db: Session = Depends(get_db)):
    q = db.query(models.Ad)
    q, start, end = _apply_ra_params(q, request)
    total = q.count()
    limit = (end - start + 1) if end is not None else 100
    items = q.offset(start).limit(limit).all()
    resp = JSONResponse([schemas.AdOut.from_orm(x).model_dump() for x in items])
    last = start + len(items) - 1 if items else start
    resp.headers["Content-Range"] = f"ads {start}-{last}/{total}"
    resp.headers["Access-Control-Expose-Headers"] = "Content-Range"
    return resp

@router.get("/{ad_id}", response_model=schemas.AdOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Ad).get(ad_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj

@router.post("", response_model=schemas.AdOut, dependencies=[Depends(admin_required)])
def create_ad(payload: schemas.AdCreate, db: Session = Depends(get_db)):
    obj = models.Ad(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{ad_id}", response_model=schemas.AdOut, dependencies=[Depends(admin_required)])
def update_ad(ad_id: int, payload: schemas.AdUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Ad).get(ad_id)
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj

@router.delete("/{ad_id}", dependencies=[Depends(admin_required)])
def delete_ad(ad_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Ad).get(ad_id)
    if not obj:
        raise HTTPException(404, "Not found")
    db.delete(obj); db.commit()
    return {"id": ad_id}
