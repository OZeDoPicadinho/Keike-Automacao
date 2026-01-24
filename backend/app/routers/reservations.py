from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app import crud, models, schemas
from backend.app.database import SessionLocal

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[schemas.Reservation])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(models.Reservation).all()


@router.post("", response_model=schemas.Reservation)
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    if reservation.start_at >= reservation.end_at:
        raise HTTPException(status_code=400, detail="Datas inválidas")
    if not crud.is_cabin_available(db, reservation.cabin_id, reservation.start_at, reservation.end_at):
        raise HTTPException(status_code=409, detail="Cabana ocupada no período")
    code = crud.generate_code(db)
    new_reservation = models.Reservation(
        **reservation.dict(),
        code=code,
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation


@router.put("/{reservation_id}/checkin", response_model=schemas.Reservation)
def check_in(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    reservation.status = "Em andamento"
    db.commit()
    db.refresh(reservation)
    return reservation


@router.put("/{reservation_id}/checkout", response_model=schemas.Reservation)
def check_out(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    reservation.status = "Finalizada"
    db.commit()
    db.refresh(reservation)
    return reservation
