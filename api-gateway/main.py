from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json


def get_forward_headers(request: Request) -> dict:
    headers = {}
    for name, value in request.headers.items():
        lower_name = name.lower()
        if lower_name.startswith("x-") or lower_name == "authorization":
            headers[name] = value
    return headers


app = FastAPI(title="API Gateway Taller Microservicios")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "hotels": os.getenv("HOTELS_SERVICE_URL", "http://hotels-service:8002"),
    "rooms": os.getenv("ROOMS_SERVICE_URL", "http://rooms-service:8003"),
    "reservations": os.getenv(
        "RESERVATIONS_SERVICE_URL", "http://reservations-service:8004"
    ),
}


def build_service_url(service_name: str, path: str) -> str:
    base_url = SERVICES[service_name].rstrip("/")
    if path == "health":
        return f"{base_url}/health"
    if not path:
        if service_name in {"hotels", "rooms", "reservations"}:
            return f"{base_url}/api/v1/{service_name}/"
        return f"{base_url}/api/v1/"
    # Always include service_name in the path for consistency
    return f"{base_url}/api/v1/{service_name}/{path}"


# Función auxiliar para procesar la respuesta del servicio
def process_response(response: requests.Response):
    if response.ok:
        try:
            return response.json()
        except (
            ValueError,
            json.JSONDecodeError,
        ):  # Captura solo errores de decodificación JSON
            return response.text
    else:
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "detail" in error_data:
                error_message = error_data["detail"]
            else:
                error_message = error_data
        except (ValueError, json.JSONDecodeError):
            error_message = response.text
        raise HTTPException(status_code=response.status_code, detail=error_message)


@router.get("/{service_name}/{path:path}")
async def forward_get(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found."
        )
    service_url = build_service_url(service_name, path)
    try:
        response = requests.get(
            service_url,
            params=request.query_params,
            headers=get_forward_headers(request),
        )
        return process_response(response)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request to {service_name}: {e}"
        )


@router.post("/{service_name}/{path:path}")
async def forward_post(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found."
        )
    service_url = build_service_url(service_name, path)
    try:
        # Get query parameters
        query_params = dict(request.query_params)
        
        # Try to get JSON body, but handle cases where body might be empty
        body = None
        try:
            body = await request.json()
        except (ValueError, json.JSONDecodeError):
            # If no JSON body, that's okay for some requests
            body = None
        
        response = requests.post(
            service_url,
            json=body,
            params=query_params,
            headers=get_forward_headers(request),
        )
        return process_response(response)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request to {service_name}: {e}"
        )


@router.put("/{service_name}/{path:path}")
async def forward_put(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found."
        )
    service_url = build_service_url(service_name, path)
    try:
        response = requests.put(
            service_url,
            json=await request.json(),
            headers=get_forward_headers(request),
        )
        return process_response(response)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request to {service_name}: {e}"
        )


@router.delete("/{service_name}/{path:path}")
async def forward_delete(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found."
        )
    service_url = build_service_url(service_name, path)
    try:
        response = requests.delete(service_url, headers=get_forward_headers(request))
        return process_response(response)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request to {service_name}: {e}"
        )


app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running."}
