import sys
sys.path.insert(0, '/root/tarea/sistema-reserva-de-hoteles/api-gateway')
from main import app

for route in app.routes:
    print(f"Path: {route.path} | Methods: {getattr(route, 'methods', 'N/A')}")
