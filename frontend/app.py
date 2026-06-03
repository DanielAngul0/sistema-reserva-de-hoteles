# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

# Obtén la URL del API Gateway desde las variables de entorno.
# Esta variable debe estar configurada en el docker-compose.yml.
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

CITIES = [
    {
        "id": "bogota",
        "country": "Colombia",
        "capital": "Bogotá",
        "description": "La capital colombiana con historia, cultura y gastronomía diversa.",
        "hotels": [
            {
                "id": "bogota-aurora",
                "name": "Hotel Aurora",
                "stars": 5,
                "price": 120,
                "description": "Ubicado en el centro, cerca de museos y restaurantes.",
            },
            {
                "id": "bogota-mirador",
                "name": "Mirador Suites",
                "stars": 4,
                "price": 85,
                "description": "Servicio premium, piscina y vista panorámica de la ciudad.",
            },
        ],
    },
    {
        "id": "washington",
        "country": "Estados Unidos",
        "capital": "Washington D.C.",
        "description": "Centro político y cultural con museos y arquitectura icónica.",
        "hotels": [
            {
                "id": "dc-capitol",
                "name": "Capitol Hotel",
                "stars": 5,
                "price": 150,
                "description": "A pasos del Capitolio y la zona de monumentos.",
            },
            {
                "id": "dc-riverside",
                "name": "Riverside Inn",
                "stars": 4,
                "price": 95,
                "description": "Cómodo y elegante, ideal para viajeros de negocios.",
            },
        ],
    },
    {
        "id": "mexico-city",
        "country": "México",
        "capital": "Ciudad de México",
        "description": "Una capital vibrante con tradición, museos y sabores únicos.",
        "hotels": [
            {
                "id": "cdmx-hacienda",
                "name": "Hacienda Real",
                "stars": 5,
                "price": 110,
                "description": "Encanto histórico en una de las zonas más seguras.",
            },
            {
                "id": "cdmx-azul",
                "name": "Hotel Azul",
                "stars": 4,
                "price": 90,
                "description": "Diseño moderno y fácil acceso a restaurantes y museos.",
            },
        ],
    },
    {
        "id": "ottawa",
        "country": "Canadá",
        "capital": "Ottawa",
        "description": "Capital tranquila con arquitectura imperial y parques amplios.",
        "hotels": [
            {
                "id": "ottawa-garden",
                "name": "Garden Palace",
                "stars": 4,
                "price": 105,
                "description": "Relajante y cerca del Canal Rideau.",
            },
            {
                "id": "ottawa-heritage",
                "name": "Heritage Hotel",
                "stars": 5,
                "price": 145,
                "description": "Hotel de lujo con servicio personalizado.",
            },
        ],
    },
    {
        "id": "brasilia",
        "country": "Brasil",
        "capital": "Brasilia",
        "description": "Diseño moderno y plazas monumentales en la capital brasileña.",
        "hotels": [
            {
                "id": "brasilia-azul",
                "name": "Azul Palace",
                "stars": 5,
                "price": 140,
                "description": "Vistas únicas de la arquitectura de Brasilia.",
            },
            {
                "id": "brasilia-serena",
                "name": "Serena Plaza",
                "stars": 4,
                "price": 98,
                "description": "Habitaciones modernas con desayuno incluido.",
            },
        ],
    },
    {
        "id": "madrid",
        "country": "España",
        "capital": "Madrid",
        "description": "La capital española con arte, vida nocturna y parques.",
        "hotels": [
            {
                "id": "madrid-prado",
                "name": "Prado Suites",
                "stars": 5,
                "price": 130,
                "description": "A minutos del Museo del Prado y el Parque del Retiro.",
            },
            {
                "id": "madrid-santana",
                "name": "Santana Hotel",
                "stars": 4,
                "price": 95,
                "description": "Ubicación central con fácil acceso al metro.",
            },
        ],
    },
    {
        "id": "tokyo",
        "country": "Japón",
        "capital": "Tokio",
        "description": "Una ciudad futurista con cultura milenaria y gastronomía de clase mundial.",
        "hotels": [
            {
                "id": "tokyo-oriental",
                "name": "Oriental Tower",
                "stars": 5,
                "price": 170,
                "description": "Gran hotel en el barrio de Shinjuku.",
            },
            {
                "id": "tokyo-sakura",
                "name": "Sakura Inn",
                "stars": 4,
                "price": 115,
                "description": "Ambiente tradicional con diseño moderno.",
            },
        ],
    },
    {
        "id": "sydney",
        "country": "Australia",
        "capital": "Sídney",
        "description": "Ciudad costera con la emblemática Ópera y playas famosas.",
        "hotels": [
            {
                "id": "sydney-bay",
                "name": "Bay View Hotel",
                "stars": 5,
                "price": 155,
                "description": "Vistas al puerto y fácil acceso a la Ópera.",
            },
            {
                "id": "sydney-coast",
                "name": "Coastline Inn",
                "stars": 4,
                "price": 100,
                "description": "Confort y servicio cerca de las playas.",
            },
        ],
    },
    {
        "id": "cairo",
        "country": "Egipto",
        "capital": "El Cairo",
        "description": "Capital histórica con monumentos antiguos y bazaars llenos de vida.",
        "hotels": [
            {
                "id": "cairo-pyramid",
                "name": "Pyramid View",
                "stars": 5,
                "price": 125,
                "description": "Hotel de lujo con vistas al río Nilo.",
            },
            {
                "id": "cairo-nile",
                "name": "Nile Comfort",
                "stars": 4,
                "price": 88,
                "description": "Experiencia tradicional y desayuno incluido.",
            },
        ],
    },
    {
        "id": "pretoria",
        "country": "Sudáfrica",
        "capital": "Pretoria",
        "description": "Capital administrativa con parques, monumentos y vida local.",
        "hotels": [
            {
                "id": "pretoria-heritage",
                "name": "Heritage Suites",
                "stars": 5,
                "price": 115,
                "description": "Lujo cercano al distrito histórico.",
            },
            {
                "id": "pretoria-garden",
                "name": "Garden Retreat",
                "stars": 4,
                "price": 82,
                "description": "Ambiente relajado con jardines amplios.",
            },
        ],
    },
]


def find_city(city_id):
    return next((city for city in CITIES if city["id"] == city_id), None)


def find_hotel(hotel_id):
    for city in CITIES:
        for hotel in city["hotels"]:
            if hotel["id"] == hotel_id:
                return hotel
    return None


@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}


def get_request_headers():
    headers = {}
    user = session.get("user")
    if user and user.get("role"):
        headers["X-User-Role"] = user["role"]
    return headers


@app.route("/")
def index():
    hotels_by_city = {}
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/hotels/hotels/")
        response.raise_for_status()
        hotels = response.json()
        for hotel in hotels:
            location = hotel.get("location")
            hotels_by_city.setdefault(location, []).append(hotel)
    except requests.exceptions.RequestException:
        hotels_by_city = None

    return render_template(
        "index.html",
        title="Reservas de Hoteles",
        cities=CITIES,
        hotels_by_city=hotels_by_city,
    )


@app.route("/city/<city_id>")
def city(city_id):
    city_data = find_city(city_id)
    if not city_data:
        return redirect(url_for("index"))

    hotels = []
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/hotels/hotels/")
        response.raise_for_status()
        all_hotels = response.json()
        hotels = [hotel for hotel in all_hotels if hotel.get("location") == city_id]
    except requests.exceptions.RequestException:
        hotels = city_data["hotels"]

    return render_template(
        "city.html",
        title=f"Hoteles en {city_data['capital']}",
        city=city_data,
        hotels=hotels,
    )


@app.route("/hotel/<hotel_id>", methods=["GET", "POST"])
def hotel_detail(hotel_id):
    hotel = None
    rooms = []
    error = None
    reservation = None

    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/hotels/hotels/{hotel_id}")
        response.raise_for_status()
        hotel = response.json()
    except requests.exceptions.RequestException:
        hotel = find_hotel(hotel_id)

    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/rooms/")
        response.raise_for_status()
        all_rooms = response.json()
        rooms = [room for room in all_rooms if room.get("hotel_id") == hotel_id]
    except requests.exceptions.RequestException:
        rooms = []

    if hotel is None:
        hotel = find_hotel(hotel_id)

    if not hotel:
        return redirect(url_for("index"))

    if request.method == "POST":
        user = session.get("user")
        if not user:
            error = "Debes iniciar sesión para crear una reserva."
        else:
            room_id = request.form.get("room_id") or hotel_id
            reservation_data = {
                "user_id": user.get("id"),
                "room_id": room_id,
                "check_in": request.form.get("check_in"),
                "check_out": request.form.get("check_out"),
            }

            try:
                response = requests.post(
                    f"{API_GATEWAY_URL}/api/v1/reservations/",
                    json=reservation_data,
                    headers=get_request_headers(),
                )
                response.raise_for_status()
                reservation = response.json()
            except requests.exceptions.RequestException as e:
                error = f"No se pudo crear la reserva: {e}"

    return render_template(
        "hotel.html",
        title=hotel["name"],
        hotel=hotel,
        rooms=rooms,
        error=error,
        reservation=reservation,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None

    if request.method == "POST":
        register_data = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }

        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/register/", json=register_data
            )
            response.raise_for_status()
            success = "Cuenta creada correctamente. Ahora puedes reservar tu hotel."
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.text:
                error = e.response.text
            else:
                error = f"No se pudo registrar el usuario: {e}"

    return render_template(
        "register.html", title="Crear Cuenta", error=error, success=success
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        login_data = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
        }
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/auth/login/", json=login_data
            )
            response.raise_for_status()
            user = response.json()
            session["user"] = user
            return redirect(url_for("index"))
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.text:
                error = e.response.text
            else:
                error = f"No se pudo iniciar sesión: {e}"
    return render_template("login.html", title="Iniciar Sesión", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    reservations = []
    error = None
    try:
        response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/reservations/",
            params={"user_id": user.get("id")},
            headers=get_request_headers(),
        )
        response.raise_for_status()
        reservations = response.json()
    except requests.exceptions.RequestException as e:
        error = f"No se pudo cargar tus reservas: {e}"

    return render_template(
        "profile.html", title="Mi Perfil", reservations=reservations, error=error
    )


@app.route("/reservation/<reservation_id>/cancel", methods=["POST"])
def cancel_reservation(reservation_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    try:
        response = requests.delete(
            f"{API_GATEWAY_URL}/api/v1/reservations/{reservation_id}",
            headers=get_request_headers(),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        pass
    return redirect(url_for("profile"))


@app.route("/reservation/<reservation_id>/edit", methods=["GET", "POST"])
def edit_reservation(reservation_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    reservation = None
    error = None
    try:
        response = requests.get(
            f"{API_GATEWAY_URL}/api/v1/reservations/{reservation_id}",
            headers=get_request_headers(),
        )
        response.raise_for_status()
        reservation = response.json()
    except requests.exceptions.RequestException as e:
        error = f"No se pudo obtener la reserva: {e}"

    if request.method == "POST" and reservation:
        update_data = {
            "user_id": reservation.get("user_id"),
            "room_id": reservation.get("room_id"),
            "check_in": request.form.get("check_in"),
            "check_out": request.form.get("check_out"),
        }
        try:
            response = requests.put(
                f"{API_GATEWAY_URL}/api/v1/reservations/{reservation_id}",
                json=update_data,
                headers=get_request_headers(),
            )
            response.raise_for_status()
            return redirect(url_for("profile"))
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.text:
                error = e.response.text
            else:
                error = f"No se pudo actualizar la reserva: {e}"

    return render_template(
        "edit_reservation.html",
        title="Editar Reserva",
        reservation=reservation,
        error=error,
    )


@app.route("/admin/hotel/create", methods=["GET", "POST"])
def create_hotel():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return redirect(url_for("index"))

    error = None
    success = None
    if request.method == "POST":
        hotel_data = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "description": request.form.get("description"),
            "stars": int(request.form.get("stars") or 0),
            "price": float(request.form.get("price") or 0),
        }
        try:
            response = requests.post(
                f"{API_GATEWAY_URL}/api/v1/hotels/hotels/",
                json=hotel_data,
                headers=get_request_headers(),
            )
            response.raise_for_status()
            success = "Hotel creado correctamente"
        except requests.exceptions.RequestException as e:
            error = f"No se pudo crear el hotel: {e}"

    return render_template(
        "create_hotel.html",
        title="Crear Hotel",
        error=error,
        success=success,
    )


@app.route("/admin/hotel/<hotel_id>/delete", methods=["POST"])
def delete_hotel(hotel_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return redirect(url_for("index"))

    try:
        response = requests.delete(
            f"{API_GATEWAY_URL}/api/v1/hotels/hotels/{hotel_id}",
            headers=get_request_headers(),
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        pass

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html", title="¿Cómo reservar?")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
