from PySide6 import QtGui, QtWidgets, QtCore


class LoadIndicator(QtWidgets.QFrame):
    rising: bool = True
    radius_min: int = 10
    radius_max: int = 20

    def __init__(self, radius_min: int = 10, radius_max: int = 20, parent=None) -> None:
        super(LoadIndicator, self).__init__(parent)

        self.radius_min = radius_min
        self.radius_max = radius_max
        self.radius = 10
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(3)

        self.setFixedHeight(radius_max*2)

    def paintEvent(self, event) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setBrush(QtGui.QColor(150, 150, 150))
        painter.setPen(QtCore.Qt.NoPen)

        painter.drawEllipse(self.width() / 2 - self.radius, self.height() / 2 - self.radius, self.radius * 2, self.
                            radius * 2)

    def self_close(self) -> None:
        self.timer.stop()
        self.close()

    def update_animation(self):
        self.radius += 0.1 if self.rising else -0.1
        if self.radius >= self.radius_max or self.radius <= self.radius_min:
            self.rising = not self.rising

        self.update()

    def size_expand(self) -> None:
        pass
