from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base


class Cabin(Base):
    __tablename__ = "cabins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    terminal_facial = Column(String, nullable=True)
    lpr_terminal = Column(String, nullable=True)
    status = Column(String, default="Disponível")

    reservations = relationship("Reservation", back_populates="cabin")


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    cabin_id = Column(Integer, ForeignKey("cabins.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, default="Reservado")
    responsible_group = Column(String, nullable=True)

    cabin = relationship("Cabin", back_populates="reservations")
    person = relationship("Person")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    cabin_id = Column(Integer, ForeignKey("cabins.id"), nullable=True)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    cabin_name = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_super_admin = Column(Boolean, default=False)


class IntegrationAccount(Base):
    __tablename__ = "integration_accounts"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    cabin_id = Column(Integer, ForeignKey("cabins.id"), nullable=True)
