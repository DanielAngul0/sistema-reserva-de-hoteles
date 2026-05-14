from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import os
from typing import List
from passlib.context import CryptContext

from .database_sql import get_db, create_db_and_tables
from .models import User, UserCreate, UserRead

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# Crea una instancia del router para organizar los endpoints
router = APIRouter()

# Define un endpoint raíz o de salud para verificar que el servicio está funcionando
@app.get("/")
def read_root():
    return {"message": "Servicio de Autenticación en funcionamiento."}

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar el estado del servicio."""
    return {"status": "ok"}

# Implementa los endpoints de tu microservicio aquí

@router.post("/register/", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login/")
def login(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not pwd_context.verify(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": db_user.id}

@router.get("/users/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Incluir el router en la aplicación principal
app.include_router(router, prefix="/api/v1")

# Crear las tablas al iniciar
create_db_and_tables()
