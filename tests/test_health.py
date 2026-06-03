from fastapi.testclient import TestClient

from services.authentication.main import app as auth_app
from services.hotels.main import app as hotels_app
from services.rooms.main import app as rooms_app
from services.reservations.main import app as reservations_app


def test_auth_health():
    client = TestClient(auth_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_hotels_health():
    client = TestClient(hotels_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rooms_health():
    client = TestClient(rooms_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_reservations_health():
    client = TestClient(reservations_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
