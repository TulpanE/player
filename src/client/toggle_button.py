from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Qt, QEvent, QRect, QPoint, QEasingCurve, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QPen


class ToggleButton(QCheckBox):
    def __init__(self, width=60, bg_color="#2d2d2d", circle_color="#a0a0a0", active_color="#fff",
                 animation_curve=QEasingCurve.Type.OutBounce):
        QCheckBox.__init__(self)
        self.setAttribute(Qt.WA_Hover)

        self.setFixedSize(width, 20)
        self.setCursor(Qt.PointingHandCursor)

        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color
        self._circle_disabled_color = "#1b1d23"

        # Adjusted initial position for a 20 height
        self._circle_position = 1
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)  # ms

        self.stateChanged.connect(self.start_transition)

        self.hovered = False

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            self.hovered = True
        elif event.type() == QEvent.HoverLeave:
            self.hovered = False
        return super().event(event)

    @Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position = pos
        self.update()

    def start_transition(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 14)  # Adjusted end value
        else:
            self.animation.setEndValue(1)
        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHints.Antialiasing)

        p.setPen(Qt.PenStyle.NoPen)
        r = QRect(0, 0, self.width(), self.height())

        p.setBrush(QColor(self._bg_color))
        p.drawRoundedRect(0, 0, r.width(), self.height(), self.height() / 2, self.height() / 2)

        if not self.isChecked():
            if self.isCheckable():
                p.setBrush(QColor(self._circle_color))
            else:
                p.setBrush(QColor(self._circle_disabled_color))
                p.setPen(QPen(QColor("#3c3c3c"), 3))
        else:
            p.setBrush(QColor(self._active_color))

        if self.hovered:
            p.setPen(QPen(QColor("#3c3c3c"), 3))
        else:
            if self.isCheckable():
                p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(self._circle_position, 3, 14, 14)  # Updated ellipse size

        p.end()
