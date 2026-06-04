import os
import sys
from unittest.mock import MagicMock

# Agregar el directorio raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Agregar cada directorio de servicio al path para permitir importaciones absolutas
SERVICE_DIRS = ["authentication", "hotels", "rooms", "reservations"]
for service in SERVICE_DIRS:
    service_path = os.path.join(os.path.dirname(__file__), "..", "services", service)
    if service_path not in sys.path:
        sys.path.insert(0, service_path)

# Variables de entorno para pruebas
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["SUPERUSER_USERNAME"] = "admin"
os.environ["SUPERUSER_EMAIL"] = "admin@example.com"
os.environ["SUPERUSER_PASSWORD"] = "admin123"

# Mocks necesarios
mock_mongo_client = MagicMock()
mock_mongo_client.get_database.return_value = MagicMock()
mock_mongo_client.get_database().get_collection.return_value = MagicMock()

sys.modules["motor.motor_asyncio"] = MagicMock()
sys.modules["motor.motor_asyncio"].AsyncIOMotorClient = MagicMock(
    return_value=mock_mongo_client
)

sys.modules["redis"] = MagicMock()
sys.modules["redis"].from_url = MagicMock(return_value=MagicMock())
