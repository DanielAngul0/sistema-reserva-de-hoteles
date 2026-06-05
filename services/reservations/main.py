from fastapi import FastAPI, APIRouter, HTTPException
import json
import uuid
from typing import List
from datetime import datetime

from database_redis import get_redis_client
from reservation_models import ReservationCreate, ReservationRead

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
def get_reservations(user_id: str = None):
    redis_client = get_redis_client()
    keys = redis_client.keys("reservation:*")
    reservations = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            res_dict = json.loads(data)
            if user_id and str(res_dict.get("user_id")) != str(user_id):
                continue
            reservations.append(ReservationRead(**res_dict))
    return reservations


@router.post("/reservations/", response_model=ReservationRead)
def create_reservation(reservation: ReservationCreate):
    redis_client = get_redis_client()
    res_id = str(uuid.uuid4())
    res_dict = reservation.dict()
    res_dict["id"] = res_id
    res_dict["status"] = "pending"
    res_dict["payment_status"] = "pending"
    res_dict["created_at"] = datetime.utcnow().isoformat()
    res_dict["check_in"] = res_dict["check_in"].isoformat()
    res_dict["check_out"] = res_dict["check_out"].isoformat()
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
        update_dict = reservation.dict()
        update_dict["check_in"] = update_dict["check_in"].isoformat()
        update_dict["check_out"] = update_dict["check_out"].isoformat()
        res_dict.update(update_dict)
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


@router.post("/reservations/{reservation_id}/pay", response_model=ReservationRead)
def process_payment(reservation_id: str):
    """Procesa el pago de una reserva"""
    redis_client = get_redis_client()
    data = redis_client.get(f"reservation:{reservation_id}")
    if data:
        res_dict = json.loads(data)
        res_dict["payment_status"] = "completed"
        res_dict["status"] = "confirmed"
        redis_client.set(f"reservation:{reservation_id}", json.dumps(res_dict))
        return ReservationRead(**res_dict)
    raise HTTPException(status_code=404, detail="Reservation not found")


# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")
