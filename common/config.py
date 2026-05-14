import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
# Esto asegura que las configuraciones se obtengan desde el entorno de ejecución,
# lo que es una buena práctica para entornos de desarrollo y producción.
load_dotenv()

# TODO: Define una clase para agrupar las configuraciones.
class Settings:
    """Clase para gestionar las configuraciones de la aplicación."""
    
    # URLs de los servicios
    # La URL del API Gateway se obtiene de las variables de entorno.
    API_GATEWAY_URL: str = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    
    # Agrega las URLs de los microservicios si son necesarias aquí.
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    HOTELS_SERVICE_URL: str = os.getenv("HOTELS_SERVICE_URL", "http://hotels-service:8002")
    ROOMS_SERVICE_URL: str = os.getenv("ROOMS_SERVICE_URL", "http://rooms-service:8003")
    RESERVATIONS_SERVICE_URL: str = os.getenv("RESERVATIONS_SERVICE_URL", "http://reservations-service:8004")

    # Agrega otras configuraciones globales.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-segura")
    ALGORITHM: str = "HS256"

# Crea una instancia de la clase de configuración.
settings = Settings()

# --------------------------------------------------------------------------
# Los estudiantes pueden importar este objeto settings en cualquier parte 
# de su código para acceder a las configuraciones de manera consistente.
# 
# Ejemplo de uso en un microservicio
# from common.config import settings
# 
# Ahora puedes acceder a las variables de configuración
# api_url = settings.API_GATEWAY_URL
# 