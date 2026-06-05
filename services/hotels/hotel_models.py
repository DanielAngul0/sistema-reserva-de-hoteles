from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime

# Modelos Pydantic para MongoDB


class Hotel(BaseModel):
    id: Optional[str] = None
    name: str
    location: str
    description: Optional[str] = None
    stars: int
    price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class HotelCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    stars: int
    price: float


class HotelRead(Hotel):
    pass
