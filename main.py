
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Header, APIRouter
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, exists

from database import get_db, init_db
from models import User

load_dotenv()
API_KEY_ENV = os.getenv("API_KEY")

if not API_KEY_ENV:

    raise RuntimeError(
        "Falta API_KEY en el entorno. Define API_KEY en .env o variable de entorno."
    )

def verify_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None):
    if x_api_key is None or x_api_key != API_KEY_ENV:
    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o ausente en header 'X-API-Key'.",
        )

class UserBase(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    user_email: EmailStr
    recommendations: list[str] = Field(default_factory=list)
    age: int | None = None
    ZIP: str | None = None

class UserCreate(UserBase):
    user_id: int 

class UserUpdate(BaseModel):

    user_name: str | None = Field(None, min_length=1, max_length=100)
    user_email: EmailStr | None = None
    recommendations: list[str] | None = None
    age: int | None = None
    ZIP: str | None = None

class UserOut(BaseModel):
    user_id: int
    user_name: str
    user_email: EmailStr
    recommendations: list[str] | None
    age: int | None
    ZIP: str | None

    model_config = {"from_attributes": True}

app = FastAPI(title="Tarea 3 - API Usuarios")
api = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

@app.on_event("startup")
def on_startup():
    init_db()


@api.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):

    email_exists = db.scalar(select(exists().where(User.user_email == payload.user_email)))
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya existe en la tabla.",
        )


    new_user = User(
        user_id=payload.user_id,
        user_name=payload.user_name,
        user_email=payload.user_email,
        recommendations=payload.recommendations or [],
        age=payload.age,
        ZIP=payload.ZIP,
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
    
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflicto al crear: verifica que user_id y email no estén repetidos.",
        )
    db.refresh(new_user)
    return new_user

@api.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")


    if payload.user_email and payload.user_email != user.user_email:
        email_exists = db.scalar(
            select(exists().where((User.user_email == payload.user_email) & (User.user_id != user_id)))
        )
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya existe en la tabla.",
            )


    if payload.user_name is not None:
        user.user_name = payload.user_name
    if payload.user_email is not None:
        user.user_email = payload.user_email
    if payload.recommendations is not None:
        user.recommendations = payload.recommendations
    if payload.age is not None:
        user.age = payload.age
    if payload.ZIP is not None:
        user.ZIP = payload.ZIP

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@api.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return user

@api.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    db.delete(user)
    db.commit()
    return None

app.include_router(api)
