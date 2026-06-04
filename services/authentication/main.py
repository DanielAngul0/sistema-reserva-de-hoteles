from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from typing import List
from passlib.context import CryptContext

from database_sql import get_db, create_db_and_tables, SessionLocal
from auth_models import User, UserCreate, UserRead, UserLogin

# Configura el contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Crea la aplicación FastAPI
app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()


# Define un endpoint raíz o de salud para verificar que el servicio está funcionando
@app.get("/")
def read_root():
    return {"message": "Servicio de Autenticación en funcionamiento."}


# Endpoint de salud para verificar el estado del servicio
@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}


# Endpoint para registrar un nuevo usuario
@router.post("/register/", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Endpoint para iniciar sesión y obtener un token
@router.post("/login/")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == credentials.username).first()
    if not db_user or not pwd_context.verify(
        credentials.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "role": db_user.role,
    }


# Endpoint para obtener la lista de usuarios
@router.get("/users/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Crea un superusuario por defecto al iniciar la aplicación
@app.on_event("startup")
def create_default_superuser():
    create_db_and_tables()
    username = os.getenv("SUPERUSER_USERNAME", "admin")
    email = os.getenv("SUPERUSER_EMAIL", "admin@example.com")
    password = os.getenv("SUPERUSER_PASSWORD", "admin123")
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == username).first():
            hashed_password = pwd_context.hash(password)
            admin_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                role="admin",
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()


# Incluye el router en la aplicación principal
app.include_router(router, prefix="/api/v1")
