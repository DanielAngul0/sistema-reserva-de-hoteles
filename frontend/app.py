# /frontend/app.py

from flask import Flask, render_template, request, redirect, url_for
import os
import requests

app = Flask(__name__)

# Obtén la URL del API Gateway desde las variables de entorno.
# Esta variable debe estar configurada en el docker-compose.yml.
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")

@app.route("/")
def index():
    """Ruta de la página de inicio."""
    
    # Haz una llamada al API Gateway para obtener datos
    try:
        response = requests.get(f"{API_GATEWAY_URL}/api/v1/hotels/hotels/")
        response.raise_for_status()
        hotels = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el API Gateway: {e}")
        hotels = []

    # Pasa los datos a la plantilla para renderizarlos.
    return render_template("index.html", title="Hoteles Disponibles", hotels=hotels)

@app.route("/new-item", methods=["GET", "POST"])
def new_item():
    """Ruta para crear un nuevo ítem."""
    if request.method == "POST":
        # Recoge los datos del formulario.
        item_data = {
            "name": request.form.get("name"),
            "location": request.form.get("location"),
            "description": request.form.get("description")
        }
        
        # Envía los datos al API Gateway para crear un nuevo recurso.
        try:
            response = requests.post(f"{API_GATEWAY_URL}/api/v1/hotels/hotels/", json=item_data)
            response.raise_for_status()
            return redirect(url_for("index"))
        except requests.exceptions.RequestException as e:
            print(f"Error al crear el ítem: {e}")
            return "Error al crear el ítem.", 500

    return render_template("form.html", title="Nuevo Ítem")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
