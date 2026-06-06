from fastapi import FastAPI, Request, HTTPException
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

    # Endpoint de salud especial
    if path == "health":
        return f"{base_url}/health"

    # Si no hay path, se usa el endpoint base del servicio
    if not path:
        # Para auth, el router está en /api/v1 directamente, pero el root es /
        if service_name == "auth":
            return f"{base_url}/"
        # Para servicios que tienen su propio prefijo /api/v1/<servicio> en su router
        if service_name in {"hotels", "rooms", "reservations"}:
            return f"{base_url}/api/v1/{service_name}/"
        return f"{base_url}/api/v1/"

    # Para cualquier otra ruta, se reenvía tal cual (sin repetir el nombre del servicio)
    # Ejemplo: register -> /api/v1/register/
    clean_path = path.lstrip("/")
    return f"{base_url}/api/v1/{clean_path}"


def parse_service_and_path(full_path: str):
    """
    Parsea el path completo para extraer el nombre del servicio y el path restante.
    Ejemplo: 'auth/register/' -> ('auth', 'register/')
    """
    parts = full_path.split("/", 1)
    service_name = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    return service_name, path


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


async def forward_request(service_name: str, path: str, request: Request):
    """Función auxiliar que forwardea el request al servicio correcto"""
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service '{service_name}' not found."
        )
    service_url = build_service_url(service_name, path)
    try:
        if request.method == "GET":
            response = requests.get(
                service_url,
                params=request.query_params,
                headers=get_forward_headers(request),
            )
        elif request.method == "POST":
            body = None
            try:
                body = await request.json()
            except (ValueError, json.JSONDecodeError):
                body = None
            response = requests.post(
                service_url,
                json=body,
                params=request.query_params,
                headers=get_forward_headers(request),
            )
        elif request.method == "PUT":
            response = requests.put(
                service_url,
                json=await request.json(),
                headers=get_forward_headers(request),
            )
        elif request.method == "DELETE":
            response = requests.delete(service_url, headers=get_forward_headers(request))
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        return process_response(response)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error forwarding request to {service_name}: {e}"
        )


# Rutas proxy para /api/v1/{service}/...
@app.get("/api/v1/{service}/{subpath:path}")
async def forward_get_path(service: str, subpath: str, request: Request):
    return await forward_request(service, subpath, request)


@app.post("/api/v1/{service}/{subpath:path}")
async def forward_post_path(service: str, subpath: str, request: Request):
    return await forward_request(service, subpath, request)


@app.put("/api/v1/{service}/{subpath:path}")
async def forward_put_path(service: str, subpath: str, request: Request):
    return await forward_request(service, subpath, request)


@app.delete("/api/v1/{service}/{subpath:path}")
async def forward_delete_path(service: str, subpath: str, request: Request):
    return await forward_request(service, subpath, request)


# Rutas proxy para /api/v1/{service}
@app.get("/api/v1/{service}")
async def forward_get_root(service: str, request: Request):
    return await forward_request(service, "", request)


@app.post("/api/v1/{service}")
async def forward_post_root(service: str, request: Request):
    return await forward_request(service, "", request)


@app.put("/api/v1/{service}")
async def forward_put_root(service: str, request: Request):
    return await forward_request(service, "", request)


@app.delete("/api/v1/{service}")
async def forward_delete_root(service: str, request: Request):
    return await forward_request(service, "", request)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API Gateway is running."}
