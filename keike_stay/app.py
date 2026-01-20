import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from keike_stay.ui.main_window import LoginWindow

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def load_styles(app: QApplication) -> None:
    font_path = ASSETS_DIR / "fonts" / "Inter-VariableFont.ttf"
    if not font_path.exists():
        font_path = ASSETS_DIR / "fonts" / "Inter-Regular.ttf"
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                app.setFont(families[0])
    qss_path = ASSETS_DIR / "styles" / "app.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


def run() -> None:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    load_styles(app)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
