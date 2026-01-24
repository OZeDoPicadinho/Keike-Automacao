from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .filter(models.User.password == payload.password)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "is_super_admin": user.is_super_admin,
    }
