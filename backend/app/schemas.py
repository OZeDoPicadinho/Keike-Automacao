from datetime import datetime
from pydantic import BaseModel


class CabinBase(BaseModel):
    name: str
    address: str
    photo_url: str | None = None
    terminal_facial: str | None = None
    lpr_terminal: str | None = None
    status: str = "Disponível"


class CabinCreate(CabinBase):
    pass


class Cabin(CabinBase):
    id: int

    class Config:
        from_attributes = True


class PersonBase(BaseModel):
    name: str
    role: str
    phone: str | None = None
    email: str | None = None


class PersonCreate(PersonBase):
    pass


class Person(PersonBase):
    id: int

    class Config:
        from_attributes = True


class ReservationBase(BaseModel):
    cabin_id: int
    person_id: int
    start_at: datetime
    end_at: datetime
    status: str = "Reservado"
    responsible_group: str | None = None


class ReservationCreate(ReservationBase):
    pass


class Reservation(ReservationBase):
    id: int
    code: str

    class Config:
        from_attributes = True


class DeviceBase(BaseModel):
    name: str
    kind: str
    cabin_id: int | None = None


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    title: str
    description: str
    cabin_name: str | None = None


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: str
    phone: str | None = None
    username: str
    role: str
    is_super_admin: bool = False


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class IntegrationAccountBase(BaseModel):
    provider: str
    username: str
    password: str
    cabin_id: int | None = None


class IntegrationAccountCreate(IntegrationAccountBase):
    pass


class IntegrationAccount(IntegrationAccountBase):
    id: int

    class Config:
        from_attributes = True
