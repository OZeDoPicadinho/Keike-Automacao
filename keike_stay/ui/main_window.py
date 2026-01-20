from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta
import random
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from keike_stay.data import AppState, Cabin, Device, Event, Person, Reservation, User
from keike_stay.services import EventService
from keike_stay.ui.helpers import cabin_pixmap


def format_dt(value: datetime) -> str:
    return value.strftime("%d/%m/%Y %H:%M")


def create_person_dialog(parent: QWidget, state: AppState) -> Optional[Person]:
    dialog = QDialog(parent)
    dialog.setWindowTitle("Nova Pessoa")
    layout = QVBoxLayout(dialog)
    name_input = QLineEdit()
    name_input.setPlaceholderText("Nome completo")
    role_input = QComboBox()
    role_input.addItems(["Hóspede", "Equipe", "Visita"])
    save_button = QPushButton("Salvar")
    save_button.setObjectName("primaryButton")
    save_button.clicked.connect(dialog.accept)
    layout.addWidget(name_input)
    layout.addWidget(role_input)
    layout.addWidget(save_button)
    if dialog.exec():
        if name_input.text().strip():
            new_person = Person(
                id=state.next_id(state.people),
                name=name_input.text().strip(),
                role=role_input.currentText(),
            )
            state.people.append(new_person)
            return new_person
    return None


class GlassCard(QFrame):
    def __init__(self, radius: int = 14, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.radius = radius
        self.setObjectName("glassCard")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(QColor(255, 255, 255, 30))
        painter.setBrush(QColor(30, 30, 35, 160))
        painter.drawRoundedRect(rect, self.radius, self.radius)


class SidebarButton(QPushButton):
    def __init__(self, text: str, icon: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        if icon:
            self.setIcon(QIcon.fromTheme(icon))
        self.setObjectName("sidebarButton")


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Keike Stay")
        self.setMinimumSize(1200, 720)
        self.setObjectName("loginWindow")
        self.state = AppState()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(30)

        header = QLabel("Keike Stay")
        header.setObjectName("loginTitle")
        subtitle = QLabel("Experiência premium em hospedagens inteligentes")
        subtitle.setObjectName("loginSubtitle")

        card = GlassCard()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(30, 30, 30, 30)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)

        toggle_button = QPushButton("Ver senha")
        toggle_button.setObjectName("ghostButton")
        toggle_button.clicked.connect(self._toggle_password)

        login_button = QPushButton("Entrar")
        login_button.setObjectName("primaryButton")
        login_button.clicked.connect(self._login)

        forgot = QPushButton("Esqueci minha senha")
        forgot.setObjectName("linkButton")

        card_layout.addWidget(QLabel("Login"))
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(toggle_button)
        card_layout.addWidget(login_button)
        card_layout.addWidget(forgot)

        layout.addStretch()
        layout.addWidget(header, alignment=Qt.AlignLeft)
        layout.addWidget(subtitle, alignment=Qt.AlignLeft)
        layout.addWidget(card, alignment=Qt.AlignLeft)
        layout.addStretch()

    def _toggle_password(self) -> None:
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def _login(self) -> None:
        username = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if username == "admin" and password == "admin@102030":
            self.close()
            self.main = MainWindow(self.state, is_super_admin=True)
            self.main.show()
        else:
            for user in self.state.users:
                if user.username == username and user.password == password:
                    self.close()
                    self.main = MainWindow(self.state, is_super_admin=False)
                    self.main.show()
                    return


class CabinCard(GlassCard):
    clicked = Signal(int)

    def __init__(self, cabin: Cabin, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.cabin = cabin
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(14, 14, 14, 14)

        image_label = QLabel()
        image_label.setPixmap(cabin_pixmap(260, 150))
        image_label.setScaledContents(True)
        image_label.setObjectName("cabinImage")
        layout.addWidget(image_label)

        title = QLabel(cabin.name)
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        guest = QLabel(f"{cabin.guest}")
        guest.setObjectName("cardSubtitle")
        layout.addWidget(guest)

        plate = QLabel(cabin.plate)
        plate.setObjectName("cardMeta")
        layout.addWidget(plate)

        date = QLabel(f"Até {format_dt(cabin.end_at)}")
        date.setObjectName("cardMeta")
        layout.addWidget(date)

        status = QLabel("AUTOMAÇÃO Ativada" if cabin.automation_active else "AUTOMAÇÃO Desativada")
        status.setObjectName("statusOn" if cabin.automation_active else "statusOff")
        layout.addWidget(status)

        btn = QPushButton(
            "Desativar Ambiente" if cabin.automation_active else "Ativar Ambiente"
        )
        btn.setObjectName("dangerButton" if cabin.automation_active else "secondaryButton")
        btn.clicked.connect(self._toggle_automation)
        layout.addWidget(btn)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.clicked.emit(self.cabin.id)

    def _toggle_automation(self) -> None:
        self.cabin.automation_active = not self.cabin.automation_active
        self.update()
        self.clicked.emit(self.cabin.id)


class EventListItem(QWidget):
    def __init__(self, event: Event, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(12)
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setObjectName("avatarCircle")
        layout.addWidget(avatar)

        info = QVBoxLayout()
        name = QLabel(event.title)
        name.setObjectName("eventTitle")
        subtitle = QLabel(event.subtitle)
        subtitle.setObjectName("eventSubtitle")
        info.addWidget(name)
        info.addWidget(subtitle)
        layout.addLayout(info)

        time_label = QLabel(event.time.strftime("%H:%M"))
        time_label.setObjectName("eventTime")
        layout.addWidget(time_label)


class DashboardPage(QWidget):
    cabin_selected = Signal(int)

    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        header = QLabel("Bem-vindo ao Keike Stay!")
        header.setObjectName("pageTitle")
        subtitle = QLabel("Gerencie e automatize as suas cabanas de forma simples e eficiente.")
        subtitle.setObjectName("pageSubtitle")

        header_wrap = QVBoxLayout()
        header_wrap.addWidget(header)
        header_wrap.addWidget(subtitle)

        header_box = QWidget()
        header_box.setLayout(header_wrap)

        layout.addWidget(header_box, 0, 0, 1, 2)

        cards_wrapper = QHBoxLayout()
        for cabin in self.state.cabins:
            card = CabinCard(cabin)
            card.clicked.connect(self.cabin_selected.emit)
            cards_wrapper.addWidget(card)

        cards_container = QWidget()
        cards_container.setLayout(cards_wrapper)
        layout.addWidget(cards_container, 1, 0, 1, 2)

        right_panel = QVBoxLayout()
        lpr_card = GlassCard()
        lpr_layout = QVBoxLayout(lpr_card)
        lpr_label = QLabel("LPR PORTÃO")
        lpr_label.setObjectName("sectionTitle")
        plate = QLabel("ABCD123")
        plate.setObjectName("lprPlate")
        status = QLabel("Portão Aberto Agora")
        status.setObjectName("lprStatus")
        lpr_layout.addWidget(lpr_label)
        lpr_layout.addWidget(plate)
        lpr_layout.addWidget(status)

        events_card = GlassCard()
        events_layout = QVBoxLayout(events_card)
        events_title = QLabel("ÚLTIMOS EVENTOS")
        events_title.setObjectName("sectionTitle")
        events_layout.addWidget(events_title)
        self.events_list = QListWidget()
        self.events_list.setObjectName("eventList")
        for event in self.state.events:
            item = QListWidgetItem()
            widget = EventListItem(event)
            item.setSizeHint(widget.sizeHint())
            self.events_list.addItem(item)
            self.events_list.setItemWidget(item, widget)
        events_layout.addWidget(self.events_list)

        right_panel.addWidget(lpr_card)
        right_panel.addWidget(events_card)
        right_panel.addStretch()

        right_container = QWidget()
        right_container.setLayout(right_panel)
        right_container.setFixedWidth(300)
        layout.addWidget(right_container, 0, 2, 2, 1)

    def push_event(self, event: Event) -> None:
        item = QListWidgetItem()
        widget = EventListItem(event)
        item.setSizeHint(widget.sizeHint())
        self.events_list.insertItem(0, item)
        self.events_list.setItemWidget(item, widget)


class CabinDetailPage(QWidget):
    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self.current_cabin: Optional[Cabin] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setSpacing(18)

        self.cabin_list = QListWidget()
        self.cabin_list.setObjectName("cabinList")
        self.cabin_list.itemClicked.connect(self._select_cabin)
        for cabin in self.state.cabins:
            item = QListWidgetItem(cabin.name)
            item.setData(Qt.UserRole, cabin.id)
            self.cabin_list.addItem(item)
        layout.addWidget(self.cabin_list, 0, 0, 2, 1)

        self.detail_card = GlassCard()
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.setSpacing(12)

        self.detail_title = QLabel("Selecione uma cabana")
        self.detail_title.setObjectName("pageTitle")
        detail_layout.addWidget(self.detail_title)

        self.automation_status = QLabel("")
        self.automation_status.setObjectName("statusOn")
        detail_layout.addWidget(self.automation_status)

        self.automation_buttons: Dict[str, QPushButton] = {}
        for label in ["Luzes", "Ar condicionado", "TV"]:
            btn = QPushButton(label)
            btn.setObjectName("toggleButton")
            btn.setCheckable(True)
            btn.clicked.connect(self._toggle_device)
            self.automation_buttons[label] = btn
            detail_layout.addWidget(btn)

        self.metric_label = QLabel("Métrica de alugueis")
        self.metric_label.setObjectName("sectionTitle")
        detail_layout.addWidget(self.metric_label)

        self.metric_bar = QFrame()
        self.metric_bar.setObjectName("metricBar")
        self.metric_bar.setFixedHeight(80)
        detail_layout.addWidget(self.metric_bar)

        self.last_guest = QLabel("Último acesso: -")
        self.last_guest.setObjectName("cardMeta")
        detail_layout.addWidget(self.last_guest)

        self.device_info = QLabel("Facial: - | LPR: -")
        self.device_info.setObjectName("cardMeta")
        detail_layout.addWidget(self.device_info)

        self.quick_reservation = QPushButton("Reserva rápida")
        self.quick_reservation.setObjectName("primaryButton")
        detail_layout.addWidget(self.quick_reservation)

        self.integration_button = QPushButton("Adicionar dispositivos (Tuya/SmartThings)")
        self.integration_button.setObjectName("secondaryButton")
        detail_layout.addWidget(self.integration_button)

        self.edit_button = QPushButton("Editar Cabana")
        self.edit_button.setObjectName("secondaryButton")
        self.edit_button.clicked.connect(self._edit_cabin)
        detail_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Deletar Cabana")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self._delete_cabin)
        detail_layout.addWidget(self.delete_button)

        layout.addWidget(self.detail_card, 0, 1, 1, 2)

    def set_cabin(self, cabin_id: int) -> None:
        for cabin in self.state.cabins:
            if cabin.id == cabin_id:
                self.current_cabin = cabin
                self.detail_title.setText(cabin.name)
                self.automation_status.setText(
                    "AUTOMAÇÃO Ativada" if cabin.automation_active else "AUTOMAÇÃO Desativada"
                )
                self.automation_buttons["Luzes"].setChecked(cabin.automations.lights)
                self.automation_buttons["Ar condicionado"].setChecked(
                    cabin.automations.climate
                )
                self.automation_buttons["TV"].setChecked(cabin.automations.tv)
                self.last_guest.setText(f"Último acesso: {cabin.guest}")
                facial = cabin.terminal_facial or "Não vinculado"
                lpr = cabin.lpr_terminal or "Não vinculado"
                self.device_info.setText(f"Facial: {facial} | LPR: {lpr}")
                return

    def _select_cabin(self, item: QListWidgetItem) -> None:
        cabin_id = item.data(Qt.UserRole)
        self.set_cabin(cabin_id)

    def _toggle_device(self) -> None:
        if not self.current_cabin:
            return
        self.current_cabin.automations.lights = self.automation_buttons["Luzes"].isChecked()
        self.current_cabin.automations.climate = self.automation_buttons[
            "Ar condicionado"
        ].isChecked()
        self.current_cabin.automations.tv = self.automation_buttons["TV"].isChecked()

    def _edit_cabin(self) -> None:
        if not self.current_cabin:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Cabana")
        layout = QVBoxLayout(dialog)
        name_input = QLineEdit(self.current_cabin.name)
        address_input = QLineEdit(self.current_cabin.address)
        facial_input = QLineEdit(self.current_cabin.terminal_facial or "")
        facial_input.setPlaceholderText("Terminal facial")
        lpr_input = QLineEdit(self.current_cabin.lpr_terminal or "")
        lpr_input.setPlaceholderText("LPR")
        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(address_input)
        layout.addWidget(facial_input)
        layout.addWidget(lpr_input)
        layout.addWidget(save_button)
        if dialog.exec():
            self.current_cabin.name = name_input.text().strip() or self.current_cabin.name
            self.current_cabin.address = address_input.text().strip()
            self.current_cabin.terminal_facial = facial_input.text().strip() or None
            self.current_cabin.lpr_terminal = lpr_input.text().strip() or None
            self.detail_title.setText(self.current_cabin.name)
            self.device_info.setText(
                f"Facial: {self.current_cabin.terminal_facial or 'Não vinculado'} | "
                f"LPR: {self.current_cabin.lpr_terminal or 'Não vinculado'}"
            )

    def _delete_cabin(self) -> None:
        if not self.current_cabin:
            return
        cabin_id = self.current_cabin.id
        self.state.cabins = [c for c in self.state.cabins if c.id != cabin_id]
        self.cabin_list.clear()
        for cabin in self.state.cabins:
            item = QListWidgetItem(cabin.name)
            item.setData(Qt.UserRole, cabin.id)
            self.cabin_list.addItem(item)
        self.current_cabin = None
        self.detail_title.setText("Selecione uma cabana")
        self.automation_status.setText("")
        self.last_guest.setText("Último acesso: -")
        self.device_info.setText("Facial: - | LPR: -")


class PeoplePage(QWidget):
    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setSpacing(16)

        self.people_list = QListWidget()
        self.people_list.setObjectName("peopleList")
        self.people_list.itemClicked.connect(self._show_detail)
        layout.addWidget(self.people_list, 0, 0, 2, 1)

        self.detail_card = GlassCard()
        detail_layout = QVBoxLayout(self.detail_card)
        self.detail_name = QLabel("Pessoa")
        self.detail_name.setObjectName("pageTitle")
        detail_layout.addWidget(self.detail_name)

        self.detail_role = QLabel("")
        self.detail_role.setObjectName("cardMeta")
        detail_layout.addWidget(self.detail_role)

        self.detail_visits = QLabel("Visitas por cabana")
        self.detail_visits.setObjectName("sectionTitle")
        detail_layout.addWidget(self.detail_visits)

        self.metric = QLabel("")
        self.metric.setObjectName("cardMeta")
        detail_layout.addWidget(self.metric)

        self.group_info = QLabel("")
        self.group_info.setObjectName("cardMeta")
        detail_layout.addWidget(self.group_info)

        self.edit_button = QPushButton("Editar Pessoa")
        self.edit_button.setObjectName("secondaryButton")
        self.edit_button.clicked.connect(self._edit_person)
        detail_layout.addWidget(self.edit_button)

        self.add_button = QPushButton("Adicionar Pessoa")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self._add_person)
        detail_layout.addWidget(self.add_button)

        layout.addWidget(self.detail_card, 0, 1, 1, 2)

        self._refresh_list()

    def _refresh_list(self) -> None:
        self.people_list.clear()
        for person in self.state.people:
            item = QListWidgetItem(f"{person.name} · {person.role}")
            item.setData(Qt.UserRole, person.id)
            self.people_list.addItem(item)

    def _show_detail(self, item: QListWidgetItem) -> None:
        person_id = item.data(Qt.UserRole)
        person = next(p for p in self.state.people if p.id == person_id)
        self.detail_name.setText(person.name)
        self.detail_role.setText(person.role)
        self.detail_name.setProperty("person_id", person.id)
        if person.visits:
            metrics = ", ".join(
                f"Cabana {cid}: {count}x" for cid, count in person.visits.items()
            )
        else:
            metrics = "Sem visitas registradas"
        self.metric.setText(metrics)
        if person.group_of:
            owner = next((p for p in self.state.people if p.id == person.group_of), None)
            if owner:
                self.group_info.setText(
                    f"Pessoa visitou a cabana fazendo parte do grupo de {owner.name}."
                )
        else:
            self.group_info.setText("")

    def _add_person(self) -> None:
        person = create_person_dialog(self, self.state)
        if person:
            self._refresh_list()
            self.detail_name.setText(person.name)
            self.detail_role.setText(person.role)
            self.metric.setText("Sem visitas registradas")

    def _edit_person(self) -> None:
        person_id = self.detail_name.property("person_id")
        if not person_id:
            return
        person = next(p for p in self.state.people if p.id == person_id)
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Pessoa")
        layout = QVBoxLayout(dialog)
        name_input = QLineEdit(person.name)
        role_input = QComboBox()
        role_input.addItems(["Hóspede", "Equipe", "Visita"])
        role_input.setCurrentText(person.role)
        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(role_input)
        layout.addWidget(save_button)
        if dialog.exec():
            person.name = name_input.text().strip() or person.name
            person.role = role_input.currentText()
            self._refresh_list()
            self.detail_name.setText(person.name)
            self.detail_role.setText(person.role)


class ReservationPage(QWidget):
    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setSpacing(16)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Buscar por código, pessoa ou período"
        )
        self.search_input.textChanged.connect(self._refresh_list)
        layout.addWidget(self.search_input, 0, 0, 1, 1)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("reservationTabs")
        self.reservation_list = QListWidget()
        self.reservation_list.setObjectName("reservationList")
        self.reservation_list.itemClicked.connect(self._show_detail)
        self.finished_list = QListWidget()
        self.finished_list.setObjectName("reservationFinishedList")
        self.finished_list.itemClicked.connect(self._show_detail)
        self.tabs.addTab(self.reservation_list, "Ativas")
        self.tabs.addTab(self.finished_list, "Finalizadas")
        layout.addWidget(self.tabs, 1, 0, 1, 1)

        self.detail_card = GlassCard()
        detail_layout = QVBoxLayout(self.detail_card)
        self.detail_title = QLabel("Reservas")
        self.detail_title.setObjectName("pageTitle")
        detail_layout.addWidget(self.detail_title)

        self.detail_info = QLabel("Selecione uma reserva")
        self.detail_info.setObjectName("cardMeta")
        detail_layout.addWidget(self.detail_info)

        self.new_button = QPushButton("Nova Reserva")
        self.new_button.setObjectName("primaryButton")
        self.new_button.clicked.connect(self._new_reservation)
        detail_layout.addWidget(self.new_button)

        layout.addWidget(self.detail_card, 0, 1, 2, 2)
        self._refresh_list()

    def _refresh_list(self) -> None:
        query = self.search_input.text().lower()
        self.reservation_list.clear()
        self.finished_list.clear()
        now = datetime.now()
        for reservation in self.state.reservations:
            person = next(p for p in self.state.people if p.id == reservation.person_id)
            cabin = next(c for c in self.state.cabins if c.id == reservation.cabin_id)
            label = (
                f"{person.name} · {reservation.code} · {format_dt(reservation.start_at)}"
            )
            if query and query not in label.lower() and query not in cabin.name.lower():
                continue
            status = "Finalizada" if reservation.end_at < now else reservation.status
            item = QListWidgetItem(f"{person.name} · {reservation.code} · {status}")
            item.setData(Qt.UserRole, reservation.id)
            if reservation.end_at < now:
                self.finished_list.addItem(item)
            else:
                self.reservation_list.addItem(item)

    def _show_detail(self, item: QListWidgetItem) -> None:
        reservation_id = item.data(Qt.UserRole)
        reservation = next(r for r in self.state.reservations if r.id == reservation_id)
        cabin = next(c for c in self.state.cabins if c.id == reservation.cabin_id)
        person = next(p for p in self.state.people if p.id == reservation.person_id)
        self.detail_info.setText(
            f"{person.name} em {cabin.name} de {format_dt(reservation.start_at)}"
            f" até {format_dt(reservation.end_at)}"
        )

    def _new_reservation(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Nova Reserva")
        layout = QVBoxLayout(dialog)
        cabin_select = QComboBox()
        for cabin in self.state.cabins:
            cabin_select.addItem(cabin.name, cabin.id)
        person_select = QComboBox()
        for person in self.state.people:
            person_select.addItem(person.name, person.id)
        start_date = QDateEdit(datetime.now())
        end_date = QDateEdit(datetime.now() + timedelta(days=1))
        start_date.setCalendarPopup(True)
        end_date.setCalendarPopup(True)

        warning = QLabel("")
        warning.setObjectName("statusOff")

        group_toggle = QPushButton("Adicionar pessoas ao grupo?")
        group_toggle.setCheckable(True)
        group_toggle.setObjectName("secondaryButton")
        group_list = QListWidget()
        group_list.setSelectionMode(QListWidget.MultiSelection)
        for person in self.state.people:
            item = QListWidgetItem(person.name)
            item.setData(Qt.UserRole, person.id)
            group_list.addItem(item)
        group_list.setVisible(False)

        add_person_button = QPushButton("Cadastro rápido de pessoa")
        add_person_button.setObjectName("linkButton")

        add_group_button = QPushButton("Adicionar pessoa ao grupo")
        add_group_button.setObjectName("linkButton")

        save_button = QPushButton("Salvar Reserva")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)

        def refresh_warning() -> None:
            cabin_id = cabin_select.currentData()
            start = datetime.combine(start_date.date().toPython(), datetime.min.time())
            end = datetime.combine(end_date.date().toPython(), datetime.min.time())
            conflict = any(
                res.cabin_id == cabin_id
                and not (end <= res.start_at or start >= res.end_at)
                for res in self.state.reservations
            )
            if conflict:
                warning.setText("Cabana ocupada no período selecionado.")
                save_button.setEnabled(False)
            else:
                warning.setText("")
                save_button.setEnabled(True)

        def add_person_quick() -> None:
            new_person = create_person_dialog(self, self.state)
            if new_person:
                person_select.addItem(new_person.name, new_person.id)
                person_select.setCurrentText(new_person.name)
                item = QListWidgetItem(new_person.name)
                item.setData(Qt.UserRole, new_person.id)
                group_list.addItem(item)

        def toggle_group() -> None:
            group_list.setVisible(group_toggle.isChecked())
            add_group_button.setVisible(group_toggle.isChecked())

        def add_group_person() -> None:
            new_person = create_person_dialog(self, self.state)
            if new_person:
                item = QListWidgetItem(new_person.name)
                item.setData(Qt.UserRole, new_person.id)
                group_list.addItem(item)

        add_person_button.clicked.connect(add_person_quick)
        add_group_button.clicked.connect(add_group_person)
        group_toggle.clicked.connect(toggle_group)

        cabin_select.currentIndexChanged.connect(refresh_warning)
        start_date.dateChanged.connect(refresh_warning)
        end_date.dateChanged.connect(refresh_warning)
        refresh_warning()

        layout.addWidget(cabin_select)
        layout.addWidget(person_select)
        layout.addWidget(add_person_button)
        layout.addWidget(start_date)
        layout.addWidget(end_date)
        layout.addWidget(warning)
        layout.addWidget(group_toggle)
        layout.addWidget(group_list)
        layout.addWidget(add_group_button)
        layout.addWidget(save_button)

        if dialog.exec():
            reservation_id = self.state.next_id(self.state.reservations)
            code = ""
            while True:
                code = f"{random.randint(0, 999999999):09d}"
                if not any(r.code == code for r in self.state.reservations):
                    break
            start_at = datetime.combine(
                start_date.date().toPython(), datetime.min.time()
            )
            end_at = datetime.combine(end_date.date().toPython(), datetime.min.time())
            new_reservation = Reservation(
                id=reservation_id,
                cabin_id=cabin_select.currentData(),
                person_id=person_select.currentData(),
                start_at=start_at,
                end_at=end_at,
                code=code,
            )
            if group_toggle.isChecked():
                group_ids = [
                    group_list.item(i).data(Qt.UserRole)
                    for i in range(group_list.count())
                    if group_list.item(i).isSelected()
                ]
                new_reservation.group_people = group_ids
                for pid in group_ids:
                    person = next(p for p in self.state.people if p.id == pid)
                    person.group_of = new_reservation.person_id
            cabin = next(c for c in self.state.cabins if c.id == new_reservation.cabin_id)
            for pid in [new_reservation.person_id] + new_reservation.group_people:
                person = next(p for p in self.state.people if p.id == pid)
                person.visits[cabin.id] = person.visits.get(cabin.id, 0) + 1
            self.state.reservations.append(new_reservation)
            self._refresh_list()


class DevicesPage(QWidget):
    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setSpacing(16)

        self.device_list = QListWidget()
        self.device_list.setObjectName("deviceList")
        self.device_list.itemClicked.connect(self._show_device)
        layout.addWidget(self.device_list, 0, 0, 2, 1)

        self.detail_card = GlassCard()
        detail_layout = QVBoxLayout(self.detail_card)
        title = QLabel("Dispositivos")
        title.setObjectName("pageTitle")
        detail_layout.addWidget(title)

        add_button = QPushButton("Adicionar Dispositivo")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self._add_device)
        detail_layout.addWidget(add_button)

        self.edit_button = QPushButton("Editar Dispositivo")
        self.edit_button.setObjectName("secondaryButton")
        self.edit_button.clicked.connect(self._edit_device)
        detail_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Deletar Dispositivo")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.clicked.connect(self._delete_device)
        detail_layout.addWidget(self.delete_button)

        self.access_title = QLabel("Níveis de acesso")
        self.access_title.setObjectName("sectionTitle")
        detail_layout.addWidget(self.access_title)

        self.access_list = QLabel("Acesso automático por cabana")
        self.access_list.setObjectName("cardMeta")
        detail_layout.addWidget(self.access_list)

        layout.addWidget(self.detail_card, 0, 1, 1, 2)
        self._refresh_list()
        self._current_device_id: Optional[int] = None

    def _refresh_list(self) -> None:
        self.device_list.clear()
        for device in self.state.devices:
            item = QListWidgetItem(f"{device.name} · {device.kind}")
            item.setData(Qt.UserRole, device.id)
            self.device_list.addItem(item)

    def _show_device(self, item: QListWidgetItem) -> None:
        self._current_device_id = item.data(Qt.UserRole)

    def _add_device(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar dispositivo")
        layout = QVBoxLayout(dialog)
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nome")
        type_select = QComboBox()
        type_select.addItems(["Terminal Facial", "LPR"])
        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(type_select)
        layout.addWidget(save_button)
        if dialog.exec():
            new_device = Device(
                id=self.state.next_id(self.state.devices),
                name=name_input.text() or "Novo dispositivo",
                kind=type_select.currentText(),
            )
            self.state.devices.append(new_device)
            self._refresh_list()

    def _edit_device(self) -> None:
        if not self._current_device_id:
            return
        device = next(d for d in self.state.devices if d.id == self._current_device_id)
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar dispositivo")
        layout = QVBoxLayout(dialog)
        name_input = QLineEdit(device.name)
        type_select = QComboBox()
        type_select.addItems(["Terminal Facial", "LPR"])
        type_select.setCurrentText(device.kind)
        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(type_select)
        layout.addWidget(save_button)
        if dialog.exec():
            device.name = name_input.text().strip() or device.name
            device.kind = type_select.currentText()
            self._refresh_list()

    def _delete_device(self) -> None:
        if not self._current_device_id:
            return
        self.state.devices = [
            d for d in self.state.devices if d.id != self._current_device_id
        ]
        self._current_device_id = None
        self._refresh_list()


class AutomationPage(QWidget):
    def __init__(self, state: AppState, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setSpacing(16)
        title = QLabel("Automação")
        title.setObjectName("pageTitle")
        layout.addWidget(title, 0, 0, 1, 2)

        self.cabin_list = QListWidget()
        for cabin in self.state.cabins:
            item = QListWidgetItem(cabin.name)
            item.setData(Qt.UserRole, cabin.id)
            self.cabin_list.addItem(item)
        layout.addWidget(self.cabin_list, 1, 0, 1, 1)

        self.detail_card = GlassCard()
        detail_layout = QVBoxLayout(self.detail_card)
        detail_layout.addWidget(QLabel("Integrações Tuya / Alexa / SmartThings"))
        connect_button = QPushButton("Conectar conta")
        connect_button.setObjectName("primaryButton")
        detail_layout.addWidget(connect_button)
        routine_button = QPushButton("Criar Rotina")
        routine_button.setObjectName("secondaryButton")
        detail_layout.addWidget(routine_button)
        layout.addWidget(self.detail_card, 1, 1, 1, 1)


class UsersPage(QWidget):
    def __init__(self, state: AppState, is_super_admin: bool, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state = state
        self.is_super_admin = is_super_admin
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Usuários")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.user_list = QListWidget()
        self.user_list.setObjectName("userList")
        layout.addWidget(self.user_list)

        self.add_button = QPushButton("Adicionar Usuário")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setEnabled(self.is_super_admin)
        self.add_button.clicked.connect(self._add_user)
        layout.addWidget(self.add_button)

        self._refresh_list()

    def _refresh_list(self) -> None:
        self.user_list.clear()
        for user in self.state.users:
            item = QListWidgetItem(f"{user.name} · {user.role}")
            self.user_list.addItem(item)

    def _add_user(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo usuário")
        layout = QVBoxLayout(dialog)
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nome completo")
        email_input = QLineEdit()
        email_input.setPlaceholderText("Email")
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Telefone")
        username_input = QLineEdit()
        username_input.setPlaceholderText("Usuário")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Senha")
        password_input.setEchoMode(QLineEdit.Password)
        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText("Confirmar senha")
        confirm_input.setEchoMode(QLineEdit.Password)
        toggle_button = QPushButton("Ver senha")
        toggle_button.setObjectName("ghostButton")
        toggle_button.clicked.connect(
            lambda: password_input.setEchoMode(
                QLineEdit.Normal
                if password_input.echoMode() == QLineEdit.Password
                else QLineEdit.Password
            )
        )
        role_input = QLineEdit()
        role_input.setPlaceholderText("Cargo")
        save_button = QPushButton("Salvar")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(dialog.accept)
        layout.addWidget(name_input)
        layout.addWidget(email_input)
        layout.addWidget(phone_input)
        layout.addWidget(username_input)
        layout.addWidget(password_input)
        layout.addWidget(confirm_input)
        layout.addWidget(toggle_button)
        layout.addWidget(role_input)
        layout.addWidget(save_button)
        if dialog.exec():
            if password_input.text() != confirm_input.text():
                return
            exists = any(
                user.email == email_input.text()
                or user.phone == phone_input.text()
                or user.username == username_input.text()
                for user in self.state.users
            )
            if exists:
                return
            self.state.users.append(
                User(
                    id=self.state.next_id(self.state.users),
                    name=name_input.text(),
                    email=email_input.text(),
                    phone=phone_input.text(),
                    username=username_input.text(),
                    password=password_input.text(),
                    role=role_input.text(),
                )
            )
            self._refresh_list()


class MainWindow(QWidget):
    def __init__(self, state: AppState, is_super_admin: bool) -> None:
        super().__init__()
        self.state = state
        self.is_super_admin = is_super_admin
        self.setWindowTitle("Keike Stay")
        self.setMinimumSize(1366, 768)
        self.setObjectName("mainWindow")
        self.event_service = EventService(self.state)
        self.event_service.event_created.connect(self._on_event)
        self._build_ui()
        self.event_service.start()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        sidebar = GlassCard()
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(16)

        logo = QLabel("Keike Stay")
        logo.setObjectName("logoTitle")
        sidebar_layout.addWidget(logo)

        self.buttons: Dict[str, SidebarButton] = {}
        menu_items = [
            ("Dashboard", "view-dashboard"),
            ("Cabanas", "home"),
            ("Pessoas", "user"),
            ("Reservas", "calendar"),
            ("Dispositivos", "devices"),
            ("Automação", "settings"),
            ("Usuários", "user-group"),
        ]
        for label, icon in menu_items:
            button = SidebarButton(label, icon)
            button.clicked.connect(lambda checked, key=label: self._switch_page(key))
            sidebar_layout.addWidget(button)
            self.buttons[label] = button

        sidebar_layout.addStretch()
        layout.addWidget(sidebar)

        content = QVBoxLayout()
        header = GlassCard()
        header_layout = QHBoxLayout(header)
        header_layout.addWidget(QLabel("Bem-vindo ao Keike Stay!"))
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Admin"))
        content.addWidget(header)

        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(self.state)
        self.dashboard_page.cabin_selected.connect(self._open_cabin_detail)
        self.cabin_detail_page = CabinDetailPage(self.state)
        self.people_page = PeoplePage(self.state)
        self.reservation_page = ReservationPage(self.state)
        self.devices_page = DevicesPage(self.state)
        self.automation_page = AutomationPage(self.state)
        self.users_page = UsersPage(self.state, self.is_super_admin)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.cabin_detail_page)
        self.stack.addWidget(self.people_page)
        self.stack.addWidget(self.reservation_page)
        self.stack.addWidget(self.devices_page)
        self.stack.addWidget(self.automation_page)
        self.stack.addWidget(self.users_page)

        content.addWidget(self.stack)
        layout.addLayout(content, 1)

        self._switch_page("Dashboard")

    def _switch_page(self, key: str) -> None:
        for label, button in self.buttons.items():
            button.setChecked(label == key)
        index = {
            "Dashboard": 0,
            "Cabanas": 1,
            "Pessoas": 2,
            "Reservas": 3,
            "Dispositivos": 4,
            "Automação": 5,
            "Usuários": 6,
        }.get(key, 0)
        self.stack.setCurrentIndex(index)

    def _open_cabin_detail(self, cabin_id: int) -> None:
        self._switch_page("Cabanas")
        self.cabin_detail_page.set_cabin(cabin_id)

    def _on_event(self, event: Event) -> None:
        self.dashboard_page.push_event(event)
