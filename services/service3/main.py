from fastapi import FastAPI, APIRouter, HTTPException
import os
import json
import uuid
from typing import List

from .database_redis import get_redis_client
from .models import Reservation, ReservationCreate, ReservationRead

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Define un endpoint raíz o de salud para verificar que el servicio está funcionando
@app.get("/")
def read_root():
    return {"message": "Servicio de Reservas en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Implementa los endpoints de tu microservicio aquí

@router.get("/reservations/", response_model=List[ReservationRead])
def get_reservations():
    redis_client = get_redis_client()
    keys = redis_client.keys("reservation:*")
    reservations = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            res_dict = json.loads(data)
            reservations.append(ReservationRead(**res_dict))
    return reservations

@router.post("/reservations/", response_model=ReservationRead)
def create_reservation(reservation: ReservationCreate):
    redis_client = get_redis_client()
    res_id = str(uuid.uuid4())
    res_dict = reservation.dict()
    res_dict["id"] = res_id
    res_dict["status"] = "pending"
    res_dict["created_at"] = res_dict.get("created_at", Reservation().created_at.isoformat())
    redis_client.set(f"reservation:{res_id}", json.dumps(res_dict))
    return ReservationRead(**res_dict)

@router.get("/reservations/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: str):
    redis_client = get_redis_client()
    data = redis_client.get(f"reservation:{reservation_id}")
    if data:
        res_dict = json.loads(data)
        return ReservationRead(**res_dict)
    raise HTTPException(status_code=404, detail="Reservation not found")

@router.put("/reservations/{reservation_id}", response_model=ReservationRead)
def update_reservation(reservation_id: str, reservation: ReservationCreate):
    redis_client = get_redis_client()
    data = redis_client.get(f"reservation:{reservation_id}")
    if data:
        res_dict = json.loads(data)
        res_dict.update(reservation.dict())
        redis_client.set(f"reservation:{reservation_id}", json.dumps(res_dict))
        return ReservationRead(**res_dict)
    raise HTTPException(status_code=404, detail="Reservation not found")

@router.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: str):
    redis_client = get_redis_client()
    result = redis_client.delete(f"reservation:{reservation_id}")
    if result:
        return {"message": "Reservation deleted"}
    raise HTTPException(status_code=404, detail="Reservation not found")

# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")
