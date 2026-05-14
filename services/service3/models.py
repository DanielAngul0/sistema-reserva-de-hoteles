from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Modelos Pydantic para Redis

class Reservation(BaseModel):
    id: Optional[str] = None
    user_id: str
    room_id: str
    check_in: datetime
    check_out: datetime
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReservationCreate(BaseModel):
    user_id: str
    room_id: str
    check_in: datetime
    check_out: datetime

class ReservationRead(Reservation):
    pass
