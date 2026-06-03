import os
import sys
from unittest.mock import MagicMock

# Configura el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ============================================
# Variables de entorno para las pruebas
# ============================================
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # Para auth y rooms
os.environ["REDIS_URL"] = "redis://localhost:6379/0"  # Para reservations (mockeado)
os.environ["SUPERUSER_USERNAME"] = "admin"
os.environ["SUPERUSER_EMAIL"] = "admin@example.com"
os.environ["SUPERUSER_PASSWORD"] = "admin123"

# ============================================
# Mocks para bases de datos externas
# ============================================

# 1. Mock para MongoDB (usado por hotels)
sys.modules["motor.motor_asyncio"] = MagicMock()
mock_mongo_client = MagicMock()
mock_mongo_client.get_database.return_value = MagicMock()
mock_mongo_client.get_database().get_collection.return_value = MagicMock()
sys.modules["motor.motor_asyncio"].AsyncIOMotorClient = MagicMock(
    return_value=mock_mongo_client
)

# 2. Mock para Redis (usado por reservations)
sys.modules["redis"] = MagicMock()
mock_redis_client = MagicMock()
sys.modules["redis"].from_url = MagicMock(return_value=mock_redis_client)

# NOTA: No mockeamos SQLAlchemy, usamos sqlite en memoria real.
