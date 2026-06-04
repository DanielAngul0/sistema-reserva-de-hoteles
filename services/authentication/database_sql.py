from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import time

from auth_models import Base

# Lee la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Configura la conexión a la base de datos y el sessionmaker
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Espera a que la base de datos esté disponible antes de continuar
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


# Crea las tablas en la base de datos si no existen
def create_db_and_tables():
    wait_for_db()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
