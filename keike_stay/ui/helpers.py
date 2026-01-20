from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap


def cabin_pixmap(width: int, height: int) -> QPixmap:
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0.0, QColor(44, 40, 42))
    gradient.setColorAt(1.0, QColor(22, 20, 22))
    painter.fillRect(0, 0, width, height, gradient)

    glow = QLinearGradient(0, 0, width, height)
    glow.setColorAt(0.0, QColor(120, 90, 60, 110))
    glow.setColorAt(1.0, QColor(10, 10, 10, 20))
    painter.fillRect(0, 0, width, height, glow)

    base = QPainterPath()
    base.moveTo(width * 0.2, height * 0.85)
    base.lineTo(width * 0.8, height * 0.85)
    base.lineTo(width * 0.65, height * 0.35)
    base.lineTo(width * 0.35, height * 0.35)
    base.closeSubpath()
    painter.setBrush(QColor(30, 26, 28))
    painter.setPen(QPen(QColor(70, 60, 60), 2))
    painter.drawPath(base)

    roof = QPainterPath()
    roof.moveTo(width * 0.18, height * 0.85)
    roof.lineTo(width * 0.5, height * 0.15)
    roof.lineTo(width * 0.82, height * 0.85)
    painter.setBrush(QColor(20, 18, 20))
    painter.setPen(QPen(QColor(90, 80, 80), 2))
    painter.drawPath(roof)

    light_rect = QRectF(width * 0.45, height * 0.55, width * 0.12, height * 0.22)
    painter.setBrush(QColor(255, 187, 120, 200))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(light_rect, 6, 6)

    dot_color = QColor(156, 255, 123, 140)
    painter.setBrush(dot_color)
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QPointF(width * 0.85, height * 0.2), 12, 12)

    painter.end()
    return pixmap
