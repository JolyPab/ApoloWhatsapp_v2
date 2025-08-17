from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    from_number: str
    body: str
    media_urls: List[str] = []

class Property(BaseModel):
    id: str
    title: str
    location: str
    operation: str  # 'venta' | 'renta'
    price: float
    url: str
    photos: List[str] = []

class Lead(BaseModel):
    phone: str
    name: Optional[str] = None
    preferred_time: Optional[str] = None
    intent: str  # 'visita' | 'consulta' | 'venta' | 'renta' | 'desconocido'
    property_id: Optional[str] = None
    note: Optional[str] = None