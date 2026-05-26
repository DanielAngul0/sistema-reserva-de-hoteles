from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import time

# Importa la base declarativa del archivo models.py
from models import Base

# Obtiene la URL de la base de datos de las variables de entorno.
DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el motor de la base de datos.
engine = create_engine(DATABASE_URL, echo=True)

# Configura la sesión de la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para esperar a que la base de datos esté disponible.
def wait_for_db(retries: int = 20, delay: int = 3):
    for attempt in range(retries):
        try:
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            return
        except OperationalError:
            if attempt + 1 == retries:
                raise
            time.sleep(delay)

# Función para crear todas las tablas en la base de datos.
def create_db_and_tables():
    """Crea todas las tablas definidas en models.py si no existen."""
    wait_for_db()
    Base.metadata.create_all(bind=engine)

# Define la dependencia para la sesión de la base de datos.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()