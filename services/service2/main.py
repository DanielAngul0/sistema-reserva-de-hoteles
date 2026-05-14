from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from typing import List

from .database_sql import get_db, create_db_and_tables
from .models import Room, RoomCreate, RoomRead

# Configurar la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Define un endpoint raíz o de salud para verificar que el servicio está funcionando
@app.get("/")
def read_root():
    return {"message": "Servicio de Habitaciones en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Implementa los endpoints de tu microservicio aquí

@router.get("/rooms/", response_model=List[RoomRead])
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return rooms

@router.post("/rooms/", response_model=RoomRead)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/rooms/{room_id}", response_model=RoomRead)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        return room
    raise HTTPException(status_code=404, detail="Room not found")

@router.put("/rooms/{room_id}", response_model=RoomRead)
def update_room(room_id: int, room: RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room:
        for key, value in room.dict().items():
            setattr(db_room, key, value)
        db.commit()
        db.refresh(db_room)
        return db_room
    raise HTTPException(status_code=404, detail="Room not found")

@router.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
        return {"message": "Room deleted"}
    raise HTTPException(status_code=404, detail="Room not found")

# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")

# Crear las tablas al iniciar
create_db_and_tables()
