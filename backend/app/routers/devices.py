from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/devices", tags=["devices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.Device])
def list_devices(db: Session = Depends(get_db)):
    return db.query(models.Device).all()


@router.post("", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    new_device = models.Device(**device.dict())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


@router.put("/{device_id}", response_model=schemas.Device)
def update_device(device_id: int, device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    for key, value in device.dict().items():
        setattr(db_device, key, value)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    db.delete(db_device)
    db.commit()
    return {"ok": True}
