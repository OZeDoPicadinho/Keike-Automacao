from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class AutomationState:
    lights: bool = True
    climate: bool = True
    tv: bool = False


@dataclass
class Cabin:
    id: int
    name: str
    guest: str
    plate: str
    end_at: datetime
    automation_active: bool = True
    status: str = "Reservado"
    avatar: str = ""
    address: str = "Estrada Vale da Serra, 1200"
    photo: str = ""
    devices: List[str] = field(default_factory=list)
    terminal_facial: str | None = None
    lpr_terminal: str | None = None
    automations: AutomationState = field(default_factory=AutomationState)


@dataclass
class Person:
    id: int
    name: str
    role: str
    avatar: str = ""
    visits: Dict[int, int] = field(default_factory=dict)
    group_of: int | None = None


@dataclass
class Reservation:
    id: int
    cabin_id: int
    person_id: int
    start_at: datetime
    end_at: datetime
    status: str = "Reservado"
    code: str = ""
    group_people: List[int] = field(default_factory=list)


@dataclass
class Device:
    id: int
    name: str
    kind: str
    cabin_id: int | None = None


@dataclass
class Event:
    id: int
    title: str
    subtitle: str
    time: datetime
    cabin: str
    avatar: str = ""


@dataclass
class User:
    id: int
    name: str
    email: str
    phone: str
    username: str
    password: str
    role: str


class AppState:
    def __init__(self) -> None:
        now = datetime.now()
        self.cabins: List[Cabin] = [
            Cabin(
                id=1,
                name="CABANA 1",
                guest="João Almeida",
                plate="ABCD123",
                end_at=now + timedelta(days=1),
                automation_active=True,
                status="Reservado",
            ),
            Cabin(
                id=2,
                name="CABANA 2",
                guest="José Vieira",
                plate="DOC3MNO",
                end_at=now + timedelta(days=2),
                automation_active=True,
                status="Reservado",
            ),
        ]
        self.people: List[Person] = [
            Person(id=1, name="João Almeida", role="Hóspede"),
            Person(id=2, name="José Vieira", role="Hóspede"),
            Person(id=3, name="Maria Lopes", role="Equipe"),
        ]
        self.reservations: List[Reservation] = [
            Reservation(
                id=1,
                cabin_id=1,
                person_id=1,
                start_at=now,
                end_at=now + timedelta(days=1),
                code="594203182",
            )
        ]
        self.devices: List[Device] = [
            Device(id=1, name="Facial 1", kind="Terminal Facial", cabin_id=1),
            Device(id=2, name="LPR 1", kind="LPR", cabin_id=1),
        ]
        self.events: List[Event] = [
            Event(
                id=1,
                title="João Almeida",
                subtitle="Entrou na CABANA 1",
                time=now,
                cabin="CABANA 1",
            ),
            Event(
                id=2,
                title="José Vieira",
                subtitle="Entrou na CABANA 2",
                time=now - timedelta(minutes=38),
                cabin="CABANA 2",
            ),
            Event(
                id=3,
                title="ABCD123",
                subtitle="Portão por :Scx.",
                time=now - timedelta(hours=1),
                cabin="PORTÃO",
            ),
        ]
        self.users: List[User] = [
            User(
                id=1,
                name="Super Admin",
                email="admin@keike.com",
                phone="000000000",
                username="admin",
                password="admin@102030",
                role="Super Admin",
            )
        ]

    def next_id(self, collection: List) -> int:
        if not collection:
            return 1
        return max(item.id for item in collection) + 1
