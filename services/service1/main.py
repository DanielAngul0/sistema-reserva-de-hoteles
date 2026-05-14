from fastapi import FastAPI, APIRouter, HTTPException
from bson import ObjectId
import os
from typing import List

from .database_mongo import get_collection
from .models import Hotel, HotelCreate, HotelRead

# Configurar la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Define un endpoint raíz o de salud para verificar que el servicio está funcionando
@app.get("/")
def read_root():
    return {"message": "Servicio de Hoteles en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Implementa los endpoints de tu microservicio aquí

@router.get("/hotels/", response_model=List[HotelRead])
async def get_hotels():
    collection = get_collection("hotels")
    hotels = []
    async for hotel in collection.find():
        hotel["id"] = str(hotel["_id"])
        del hotel["_id"]
        hotels.append(HotelRead(**hotel))
    return hotels

@router.post("/hotels/", response_model=HotelRead)
async def create_hotel(hotel: HotelCreate):
    collection = get_collection("hotels")
    hotel_dict = hotel.dict()
    result = await collection.insert_one(hotel_dict)
    hotel_dict["id"] = str(result.inserted_id)
    return HotelRead(**hotel_dict)

@router.get("/hotels/{hotel_id}", response_model=HotelRead)
async def get_hotel(hotel_id: str):
    collection = get_collection("hotels")
    hotel = await collection.find_one({"_id": ObjectId(hotel_id)})
    if hotel:
        hotel["id"] = str(hotel["_id"])
        del hotel["_id"]
        return HotelRead(**hotel)
    raise HTTPException(status_code=404, detail="Hotel not found")

@router.put("/hotels/{hotel_id}", response_model=HotelRead)
async def update_hotel(hotel_id: str, hotel: HotelCreate):
    collection = get_collection("hotels")
    hotel_dict = hotel.dict()
    result = await collection.update_one({"_id": ObjectId(hotel_id)}, {"$set": hotel_dict})
    if result.modified_count == 1:
        hotel_dict["id"] = hotel_id
        return HotelRead(**hotel_dict)
    raise HTTPException(status_code=404, detail="Hotel not found")

@router.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: str):
    collection = get_collection("hotels")
    result = await collection.delete_one({"_id": ObjectId(hotel_id)})
    if result.deleted_count == 1:
        return {"message": "Hotel deleted"}
    raise HTTPException(status_code=404, detail="Hotel not found")

# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")
