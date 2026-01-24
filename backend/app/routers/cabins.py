from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/cabins", tags=["cabins"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.Cabin])
def list_cabins(db: Session = Depends(get_db)):
    return db.query(models.Cabin).all()


@router.post("", response_model=schemas.Cabin)
def create_cabin(cabin: schemas.CabinCreate, db: Session = Depends(get_db)):
    new_cabin = models.Cabin(**cabin.dict())
    db.add(new_cabin)
    db.commit()
    db.refresh(new_cabin)
    return new_cabin


@router.put("/{cabin_id}", response_model=schemas.Cabin)
def update_cabin(cabin_id: int, cabin: schemas.CabinCreate, db: Session = Depends(get_db)):
    db_cabin = db.query(models.Cabin).filter(models.Cabin.id == cabin_id).first()
    if not db_cabin:
        raise HTTPException(status_code=404, detail="Cabana não encontrada")
    for key, value in cabin.dict().items():
        setattr(db_cabin, key, value)
    db.commit()
    db.refresh(db_cabin)
    return db_cabin


@router.delete("/{cabin_id}")
def delete_cabin(cabin_id: int, db: Session = Depends(get_db)):
    db_cabin = db.query(models.Cabin).filter(models.Cabin.id == cabin_id).first()
    if not db_cabin:
        raise HTTPException(status_code=404, detail="Cabana não encontrada")
    db.delete(db_cabin)
    db.commit()
    return {"ok": True}
