from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.IntegrationAccount])
def list_integrations(db: Session = Depends(get_db)):
    return db.query(models.IntegrationAccount).all()


@router.post("", response_model=schemas.IntegrationAccount)
def create_integration(account: schemas.IntegrationAccountCreate, db: Session = Depends(get_db)):
    new_account = models.IntegrationAccount(**account.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
