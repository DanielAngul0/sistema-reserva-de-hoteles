from fastapi import FastAPI, APIRouter, HTTPException, Request
import os
from typing import List

from .database_mongo import get_collection
from .models import HotelCreate, HotelRead

# Configurar la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

HOTEL_SEED = [
    {
        "_id": "bogota-aurora",
        "name": "Hotel Aurora",
        "location": "bogota",
        "description": "Ubicado en el centro, cerca de museos y restaurantes.",
        "stars": 5,
        "price": 120,
    },
    {
        "_id": "bogota-mirador",
        "name": "Mirador Suites",
        "location": "bogota",
        "description": "Servicio premium, piscina y vista panorámica de la ciudad.",
        "stars": 4,
        "price": 85,
    },
    {
        "_id": "dc-capitol",
        "name": "Capitol Hotel",
        "location": "washington",
        "description": "A pasos del Capitolio y la zona de monumentos.",
        "stars": 5,
        "price": 150,
    },
    {
        "_id": "dc-riverside",
        "name": "Riverside Inn",
        "location": "washington",
        "description": "Cómodo y elegante, ideal para viajeros de negocios.",
        "stars": 4,
        "price": 95,
    },
    {
        "_id": "cdmx-hacienda",
        "name": "Hacienda Real",
        "location": "mexico-city",
        "description": "Encanto histórico en una de las zonas más seguras.",
        "stars": 5,
        "price": 110,
    },
    {
        "_id": "cdmx-azul",
        "name": "Hotel Azul",
        "location": "mexico-city",
        "description": "Diseño moderno y fácil acceso a restaurantes y museos.",
        "stars": 4,
        "price": 90,
    },
    {
        "_id": "ottawa-garden",
        "name": "Garden Palace",
        "location": "ottawa",
        "description": "Relajante y cerca del Canal Rideau.",
        "stars": 4,
        "price": 105,
    },
    {
        "_id": "ottawa-heritage",
        "name": "Heritage Hotel",
        "location": "ottawa",
        "description": "Hotel de lujo con servicio personalizado.",
        "stars": 5,
        "price": 145,
    },
    {
        "_id": "brasilia-azul",
        "name": "Azul Palace",
        "location": "brasilia",
        "description": "Vistas únicas de la arquitectura de Brasilia.",
        "stars": 5,
        "price": 140,
    },
    {
        "_id": "brasilia-serena",
        "name": "Serena Plaza",
        "location": "brasilia",
        "description": "Habitaciones modernas con desayuno incluido.",
        "stars": 4,
        "price": 98,
    },
    {
        "_id": "madrid-prado",
        "name": "Prado Suites",
        "location": "madrid",
        "description": "A minutos del Museo del Prado y el Parque del Retiro.",
        "stars": 5,
        "price": 130,
    },
    {
        "_id": "madrid-santana",
        "name": "Santana Hotel",
        "location": "madrid",
        "description": "Ubicación central con fácil acceso al metro.",
        "stars": 4,
        "price": 95,
    },
    {
        "_id": "tokyo-oriental",
        "name": "Oriental Tower",
        "location": "tokyo",
        "description": "Gran hotel en el barrio de Shinjuku.",
        "stars": 5,
        "price": 170,
    },
    {
        "_id": "tokyo-sakura",
        "name": "Sakura Inn",
        "location": "tokyo",
        "description": "Ambiente tradicional con diseño moderno.",
        "stars": 4,
        "price": 115,
    },
    {
        "_id": "sydney-bay",
        "name": "Bay View Hotel",
        "location": "sydney",
        "description": "Vistas al puerto y fácil acceso a la Ópera.",
        "stars": 5,
        "price": 155,
    },
    {
        "_id": "sydney-coast",
        "name": "Coastline Inn",
        "location": "sydney",
        "description": "Confort y servicio cerca de las playas.",
        "stars": 4,
        "price": 100,
    },
    {
        "_id": "cairo-pyramid",
        "name": "Pyramid View",
        "location": "cairo",
        "description": "Hotel de lujo con vistas al río Nilo.",
        "stars": 5,
        "price": 125,
    },
    {
        "_id": "cairo-nile",
        "name": "Nile Comfort",
        "location": "cairo",
        "description": "Experiencia tradicional y desayuno incluido.",
        "stars": 4,
        "price": 88,
    },
    {
        "_id": "pretoria-heritage",
        "name": "Heritage Suites",
        "location": "pretoria",
        "description": "Lujo cercano al distrito histórico.",
        "stars": 5,
        "price": 115,
    },
    {
        "_id": "pretoria-garden",
        "name": "Garden Retreat",
        "location": "pretoria",
        "description": "Ambiente relajado con jardines amplios.",
        "stars": 4,
        "price": 82,
    },
]


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


def verify_admin(request: Request):
    role = request.headers.get("x-user-role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")


@router.post("/hotels/", response_model=HotelRead)
async def create_hotel(hotel: HotelCreate, request: Request):
    verify_admin(request)
    collection = get_collection("hotels")
    hotel_dict = hotel.dict()
    result = await collection.insert_one(hotel_dict)
    hotel_dict["id"] = str(result.inserted_id)
    return HotelRead(**hotel_dict)


@router.get("/hotels/{hotel_id}", response_model=HotelRead)
async def get_hotel(hotel_id: str):
    collection = get_collection("hotels")
    hotel = await collection.find_one({"_id": hotel_id})
    if hotel:
        hotel["id"] = str(hotel["_id"])
        del hotel["_id"]
        return HotelRead(**hotel)
    raise HTTPException(status_code=404, detail="Hotel not found")


@router.put("/hotels/{hotel_id}", response_model=HotelRead)
async def update_hotel(hotel_id: str, hotel: HotelCreate, request: Request):
    verify_admin(request)
    collection = get_collection("hotels")
    hotel_dict = hotel.dict()
    result = await collection.update_one({"_id": hotel_id}, {"$set": hotel_dict})
    if result.modified_count == 1:
        hotel_dict["id"] = hotel_id
        return HotelRead(**hotel_dict)
    raise HTTPException(status_code=404, detail="Hotel not found")


@router.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: str, request: Request):
    verify_admin(request)
    collection = get_collection("hotels")
    result = await collection.delete_one({"_id": hotel_id})
    if result.deleted_count == 1:
        return {"message": "Hotel deleted"}
    raise HTTPException(status_code=404, detail="Hotel not found")


@app.on_event("startup")
async def seed_hotels():
    collection = get_collection("hotels")
    count = await collection.count_documents({})
    if count == 0:
        await collection.insert_many(HOTEL_SEED)


# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")
