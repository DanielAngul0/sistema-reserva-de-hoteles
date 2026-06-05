from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from typing import List

from database_sql import get_db, create_db_and_tables
from room_models import Room, RoomCreate, RoomRead

# Configurar la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

ROOM_SEED = [
    {
        "hotel_id": "bogota-aurora",
        "room_type": "Estándar",
        "price": 95.0,
        "available": 5,
    },
    {
        "hotel_id": "bogota-aurora",
        "room_type": "Premium",
        "price": 140.0,
        "available": 4,
    },
    {
        "hotel_id": "bogota-aurora",
        "room_type": "Platino",
        "price": 180.0,
        "available": 3,
    },
    {
        "hotel_id": "bogota-mirador",
        "room_type": "Estándar",
        "price": 75.0,
        "available": 6,
    },
    {
        "hotel_id": "bogota-mirador",
        "room_type": "Premium",
        "price": 95.0,
        "available": 5,
    },
    {
        "hotel_id": "bogota-mirador",
        "room_type": "Platino",
        "price": 125.0,
        "available": 3,
    },
    {
        "hotel_id": "dc-capitol",
        "room_type": "Estándar",
        "price": 120.0,
        "available": 6,
    },
    {
        "hotel_id": "dc-capitol",
        "room_type": "Premium",
        "price": 160.0,
        "available": 4,
    },
    {
        "hotel_id": "dc-capitol",
        "room_type": "Platino",
        "price": 210.0,
        "available": 2,
    },
    {
        "hotel_id": "dc-riverside",
        "room_type": "Estándar",
        "price": 85.0,
        "available": 6,
    },
    {
        "hotel_id": "dc-riverside",
        "room_type": "Premium",
        "price": 120.0,
        "available": 4,
    },
    {
        "hotel_id": "dc-riverside",
        "room_type": "Platino",
        "price": 155.0,
        "available": 2,
    },
    {
        "hotel_id": "cdmx-hacienda",
        "room_type": "Estándar",
        "price": 110.0,
        "available": 5,
    },
    {
        "hotel_id": "cdmx-hacienda",
        "room_type": "Premium",
        "price": 155.0,
        "available": 4,
    },
    {
        "hotel_id": "cdmx-hacienda",
        "room_type": "Platino",
        "price": 200.0,
        "available": 2,
    },
    {
        "hotel_id": "cdmx-azul",
        "room_type": "Estándar",
        "price": 80.0,
        "available": 7,
    },
    {
        "hotel_id": "cdmx-azul",
        "room_type": "Premium",
        "price": 105.0,
        "available": 6,
    },
    {
        "hotel_id": "cdmx-azul",
        "room_type": "Platino",
        "price": 140.0,
        "available": 3,
    },
    {
        "hotel_id": "ottawa-garden",
        "room_type": "Estándar",
        "price": 85.0,
        "available": 6,
    },
    {
        "hotel_id": "ottawa-garden",
        "room_type": "Premium",
        "price": 110.0,
        "available": 5,
    },
    {
        "hotel_id": "ottawa-garden",
        "room_type": "Platino",
        "price": 145.0,
        "available": 3,
    },
    {
        "hotel_id": "ottawa-heritage",
        "room_type": "Estándar",
        "price": 110.0,
        "available": 5,
    },
    {
        "hotel_id": "ottawa-heritage",
        "room_type": "Premium",
        "price": 140.0,
        "available": 4,
    },
    {
        "hotel_id": "ottawa-heritage",
        "room_type": "Platino",
        "price": 160.0,
        "available": 3,
    },
    {
        "hotel_id": "brasilia-azul",
        "room_type": "Estándar",
        "price": 105.0,
        "available": 6,
    },
    {
        "hotel_id": "brasilia-azul",
        "room_type": "Premium",
        "price": 140.0,
        "available": 4,
    },
    {
        "hotel_id": "brasilia-azul",
        "room_type": "Platino",
        "price": 170.0,
        "available": 3,
    },
    {
        "hotel_id": "brasilia-serena",
        "room_type": "Estándar",
        "price": 75.0,
        "available": 7,
    },
    {
        "hotel_id": "brasilia-serena",
        "room_type": "Premium",
        "price": 100.0,
        "available": 6,
    },
    {
        "hotel_id": "brasilia-serena",
        "room_type": "Platino",
        "price": 130.0,
        "available": 3,
    },
    {
        "hotel_id": "madrid-prado",
        "room_type": "Estándar",
        "price": 100.0,
        "available": 5,
    },
    {
        "hotel_id": "madrid-prado",
        "room_type": "Premium",
        "price": 125.0,
        "available": 4,
    },
    {
        "hotel_id": "madrid-prado",
        "room_type": "Platino",
        "price": 140.0,
        "available": 3,
    },
    {
        "hotel_id": "madrid-santana",
        "room_type": "Estándar",
        "price": 75.0,
        "available": 6,
    },
    {
        "hotel_id": "madrid-santana",
        "room_type": "Premium",
        "price": 98.0,
        "available": 5,
    },
    {
        "hotel_id": "madrid-santana",
        "room_type": "Platino",
        "price": 120.0,
        "available": 3,
    },
    {
        "hotel_id": "tokyo-oriental",
        "room_type": "Estándar",
        "price": 130.0,
        "available": 5,
    },
    {
        "hotel_id": "tokyo-oriental",
        "room_type": "Premium",
        "price": 160.0,
        "available": 3,
    },
    {
        "hotel_id": "tokyo-oriental",
        "room_type": "Platino",
        "price": 190.0,
        "available": 2,
    },
    {
        "hotel_id": "tokyo-sakura",
        "room_type": "Estándar",
        "price": 90.0,
        "available": 6,
    },
    {
        "hotel_id": "tokyo-sakura",
        "room_type": "Premium",
        "price": 120.0,
        "available": 4,
    },
    {
        "hotel_id": "tokyo-sakura",
        "room_type": "Platino",
        "price": 150.0,
        "available": 2,
    },
    {
        "hotel_id": "sydney-bay",
        "room_type": "Estándar",
        "price": 115.0,
        "available": 5,
    },
    {
        "hotel_id": "sydney-bay",
        "room_type": "Premium",
        "price": 150.0,
        "available": 4,
    },
    {
        "hotel_id": "sydney-bay",
        "room_type": "Platino",
        "price": 180.0,
        "available": 3,
    },
    {
        "hotel_id": "sydney-coast",
        "room_type": "Estándar",
        "price": 85.0,
        "available": 6,
    },
    {
        "hotel_id": "sydney-coast",
        "room_type": "Premium",
        "price": 110.0,
        "available": 5,
    },
    {
        "hotel_id": "sydney-coast",
        "room_type": "Platino",
        "price": 140.0,
        "available": 3,
    },
    {
        "hotel_id": "cairo-pyramid",
        "room_type": "Estándar",
        "price": 95.0,
        "available": 5,
    },
    {
        "hotel_id": "cairo-pyramid",
        "room_type": "Premium",
        "price": 115.0,
        "available": 4,
    },
    {
        "hotel_id": "cairo-pyramid",
        "room_type": "Platino",
        "price": 135.0,
        "available": 2,
    },
    {
        "hotel_id": "cairo-nile",
        "room_type": "Estándar",
        "price": 70.0,
        "available": 7,
    },
    {
        "hotel_id": "cairo-nile",
        "room_type": "Premium",
        "price": 90.0,
        "available": 6,
    },
    {
        "hotel_id": "cairo-nile",
        "room_type": "Platino",
        "price": 110.0,
        "available": 3,
    },
    {
        "hotel_id": "pretoria-heritage",
        "room_type": "Estándar",
        "price": 90.0,
        "available": 5,
    },
    {
        "hotel_id": "pretoria-heritage",
        "room_type": "Premium",
        "price": 110.0,
        "available": 4,
    },
    {
        "hotel_id": "pretoria-heritage",
        "room_type": "Platino",
        "price": 125.0,
        "available": 3,
    },
    {
        "hotel_id": "pretoria-garden",
        "room_type": "Estándar",
        "price": 70.0,
        "available": 6,
    },
    {
        "hotel_id": "pretoria-garden",
        "room_type": "Premium",
        "price": 89.0,
        "available": 5,
    },
    {
        "hotel_id": "pretoria-garden",
        "room_type": "Platino",
        "price": 110.0,
        "available": 3,
    },
]


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


# Crear las tablas al iniciar y cargar datos de ejemplo.
@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    db = next(get_db())
    try:
        room_count = db.query(Room).count()
        if room_count == 0:
            for room_data in ROOM_SEED:
                room = Room(**room_data)
                db.add(room)
            db.commit()
    finally:
        db.close()
