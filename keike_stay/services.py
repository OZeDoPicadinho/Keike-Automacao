from __future__ import annotations

from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Signal

from keike_stay.data import AppState, Event


class EventService(QObject):
    event_created = Signal(Event)

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.timer = QTimer(self)
        self.timer.setInterval(9000)
        self.timer.timeout.connect(self._tick)

    def start(self) -> None:
        self.timer.start()

    def _tick(self) -> None:
        now = datetime.now()
        cabin = self.state.cabins[0]
        event = Event(
            id=self.state.next_id(self.state.events),
            title=cabin.plate,
            subtitle="Portão Aberto Agora",
            time=now,
            cabin="PORTÃO",
        )
        self.state.events.insert(0, event)
        self.event_created.emit(event)
