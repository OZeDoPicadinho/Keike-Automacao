from datetime import datetime
import random

from sqlalchemy.orm import Session

from backend.app import models


def create_cabin(db: Session, cabin: models.Cabin) -> models.Cabin:
    db.add(cabin)
    db.commit()
    db.refresh(cabin)
    return cabin


def create_person(db: Session, person: models.Person) -> models.Person:
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def create_reservation(db: Session, reservation: models.Reservation) -> models.Reservation:
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def generate_code(db: Session) -> str:
    while True:
        code = f"{random.randint(0, 999999999):09d}"
        exists = db.query(models.Reservation).filter(models.Reservation.code == code).first()
        if not exists:
            return code


def is_cabin_available(db: Session, cabin_id: int, start_at: datetime, end_at: datetime) -> bool:
    conflict = (
        db.query(models.Reservation)
        .filter(models.Reservation.cabin_id == cabin_id)
        .filter(models.Reservation.end_at > start_at)
        .filter(models.Reservation.start_at < end_at)
        .first()
    )
    return conflict is None
