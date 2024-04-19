from PySide6 import QtWidgets, QtCore


class AnimatedPanel(QtWidgets.QFrame):
    main_layout: QtWidgets.QVBoxLayout = None
    animator: QtCore.QPropertyAnimation = None
    animator_pos: QtCore.QPropertyAnimation = None

    def __init__(self, parent) -> None:
        super(AnimatedPanel, self).__init__(parent)
        self.init_ui()
        self.hide()

    def init_ui(self) -> None:
        self.main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)

        self.animator: QtCore.QPropertyAnimation = QtCore.QPropertyAnimation(self, b'size')
        self.animator_pos: QtCore.QPropertyAnimation = QtCore.QPropertyAnimation(self, b'pos')
        self.animator.setTargetObject(self)
        self.animator_pos.setTargetObject(self)
        self.animator.setDuration(200)
        self.animator_pos.setDuration(200)

    def show_with_anim(self) -> None:
        self.show()
        self.animator.setStartValue(QtCore.QSize(self.parent().width() - 20, 0))
        self.animator.setEndValue(QtCore.QSize(self.parent().width() - 20, self.parent().height() - 70))

        self.animator_pos.setStartValue(QtCore.QPoint(10, self.parent().height() - 70))
        self.animator_pos.setEndValue(QtCore.QPoint(10, 10))

        self.animator.start()
        self.animator_pos.start()

    def hide_with_anim(self) -> None:
        self.animator.setStartValue(QtCore.QSize(self.parent().width() - 20, self.parent().height() - 70))
        self.animator.setEndValue(QtCore.QSize(self.parent().width() - 20, 0))

        self.animator_pos.setStartValue(QtCore.QPoint(10, 10))
        self.animator_pos.setEndValue(QtCore.QPoint(10, self.parent().height() - 70))

        self.animator.start()
        self.animator_pos.start()
        self.animator.finished.connect(self.call_on_anim_end)

    def call_on_anim_end(self) -> None:
        self.animator.finished.disconnect(self.call_on_anim_end)
        self.hide()

    def size_expand(self) -> None:
        self.resize(self.parent().width() - 20, self.parent().height() - 70)
