from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os


def get_forward_headers(request: Request) -> dict:
    headers = {}
    for name, value in request.headers.items():
        lower_name = name.lower()
        if lower_name.startswith("x-") or lower_name == "authorization":
            headers[name] = value
    return headers

# Define la instancia de la aplicación FastAPI.
app = FastAPI(title="API Gateway Taller Microservicios")

# Configura CORS (Cross-Origin Resource Sharing).
# Esto es esencial para permitir que el frontend se comunique con el gateway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen (ajustar en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea un enrutador para las peticiones de los microservicios.
router = APIRouter(prefix="/api/v1")

# Define los microservicios y sus URLs.
# La URL debe coincidir con el nombre del servicio definido en docker-compose.yml.
# El puerto debe ser el del contenedor (ej. auth-service:8001).
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "hotels": os.getenv("HOTELS_SERVICE_URL", "http://hotels-service:8002"),
    "rooms": os.getenv("ROOMS_SERVICE_URL", "http://rooms-service:8003"),
    "reservations": os.getenv("RESERVATIONS_SERVICE_URL", "http://reservations-service:8004"),
}

# TODO: Implementa una ruta genérica para redirigir peticiones GET.
def build_service_url(service_name: str, path: str) -> str:
    base_url = SERVICES[service_name].rstrip("/")

    if path == "health":
        return f"{base_url}/health"

    if not path:
        if service_name in {"hotels", "rooms", "reservations"}:
            return f"{base_url}/api/v1/{service_name}/"
        return f"{base_url}/api/v1/"

    return f"{base_url}/api/v1/{path}"

@router.get("/{service_name}/{path:path}")
async def forward_get(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = build_service_url(service_name, path)

    try:
        response = requests.get(service_url, params=request.query_params, headers=get_forward_headers(request))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.post("/{service_name}/{path:path}")
async def forward_post(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = build_service_url(service_name, path)

    try:
        response = requests.post(
            service_url,
            json=await request.json(),
            headers=get_forward_headers(request),
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.put("/{service_name}/{path:path}")
async def forward_put(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = build_service_url(service_name, path)

    try:
        response = requests.put(
            service_url,
            json=await request.json(),
            headers=get_forward_headers(request),
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

@router.delete("/{service_name}/{path:path}")
async def forward_delete(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found.")

    service_url = build_service_url(service_name, path)

    try:
        response = requests.delete(service_url, headers=get_forward_headers(request))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error forwarding request to {service_name}: {e}")

# TODO: Agrega más rutas para otros métodos HTTP (PUT, DELETE, etc.).

# Incluye el router en la aplicación principal.
app.include_router(router)

# Endpoint de salud para verificar el estado del gateway.
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running."}
