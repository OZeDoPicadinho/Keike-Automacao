from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/people", tags=["people"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.Person])
def list_people(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@router.post("", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    new_person = models.Person(**person.dict())
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person


@router.put("/{person_id}", response_model=schemas.Person)
def update_person(person_id: int, person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    for key, value in person.dict().items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    return db_person


@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    db.delete(db_person)
    db.commit()
    return {"ok": True}
