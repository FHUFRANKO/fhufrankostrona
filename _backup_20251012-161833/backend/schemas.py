from pydantic import BaseModel
from typing import Optional

class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    city: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

class AdCreate(AdBase):
    pass

class AdUpdate(AdBase):
    pass

class AdOut(AdBase):
    id: int
    class Config:
        from_attributes = True
