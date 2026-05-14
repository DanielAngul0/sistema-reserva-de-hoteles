from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Modelos Pydantic para MongoDB

class Hotel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    location: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HotelCreate(BaseModel):
    name: str
    location: str
    description: Optional[str] = None

class HotelRead(Hotel):
    pass
