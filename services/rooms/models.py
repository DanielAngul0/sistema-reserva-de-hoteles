from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

# Define la base declarativa
Base = declarative_base()


# Crea tus modelos de datos aquí.
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(String, index=True)
    room_type = Column(String)
    price = Column(Float)
    available = Column(Integer, default=1)  # number available
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Room(id={self.id}, hotel_id='{self.hotel_id}', room_type='{self.room_type}')>"


# Define los modelos Pydantic para la validación de datos.


class RoomBase(BaseModel):
    hotel_id: str
    room_type: str
    price: float
    available: Optional[int] = 1


class RoomCreate(RoomBase):
    pass


class RoomRead(RoomBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
