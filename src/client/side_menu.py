from PySide6 import QtWidgets, QtCore, QtGui
from src.client.tools.style_setter import set_style_sheet
import settings
from typing import Callable
import src.client.resources_rc


class SideMenu(QtWidgets.QFrame):
    def __init__(self) -> None:
        super(SideMenu, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setObjectName("SideMenu")
        set_style_sheet(self, 'side_menu.qss')

        main_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()

        self.setLayout(main_layout)

        icon_size: QtCore.QSize = QtCore.QSize(20, 20)

        self.repeat_button: SideButton = SideButton('repeat', icon_size, self.on_repeat_click)
        self.randomize_button: SideButton = SideButton('randomize', icon_size, self.on_randomize_click)
        self.play_list_button: SideButton = SideButton('playlist', icon_size, self.on_play_list_pressed)
        self.settings_button: SideButton = SideButton('settings', icon_size, self.on_settings_pressed)

        main_layout.addWidget(self.repeat_button)
        main_layout.addWidget(self.randomize_button)
        main_layout.addWidget(self.play_list_button)
        main_layout.addWidget(self.settings_button)

    def toggle_pressed(self, sender):
        sender: SideButton = self.sender() if sender is None else sender
        sender.state = not sender.state
        sender.setIcon(
            QtGui.QPixmap(f':/img/{sender.pixmap_name}{"_pressed" if sender.state else ""}.png')
        )

    def on_repeat_click(self) -> None:
        self.toggle_pressed(self.repeat_button)

    def on_randomize_click(self) -> None:
        self.toggle_pressed(self.randomize_button)

    def on_play_list_pressed(self) -> None:
        self.toggle_pressed(self.play_list_button)
        self.parent().play_list_menu.reload()

        if self.play_list_button.state:
            if self.settings_button.state:
                self.toggle_pressed(self.settings_button)
                self.parent().settings_menu.hide_with_anim()
                self.timer: QtCore.QTimer = QtCore.QTimer(self)
                self.timer.timeout.connect(lambda: self.on_timer_finished(self.parent().play_list_menu))
                self.timer.start(300)
            else:
                self.parent().play_list_menu.show_with_anim()
        else:
            self.parent().play_list_menu.hide_with_anim()

    def on_settings_pressed(self) -> None:
        self.toggle_pressed(self.settings_button)
        self.parent().settings_menu.reload()

        if self.settings_button.state:
            if self.play_list_button.state:
                self.toggle_pressed(self.play_list_button)
                self.parent().play_list_menu.hide_with_anim()
                self.timer: QtCore.QTimer = QtCore.QTimer(self)
                self.timer.timeout.connect(lambda: self.on_timer_finished(self.parent().settings_menu))
                self.timer.start(300)

            else:
                self.parent().settings_menu.show_with_anim()
        else:
            self.parent().settings_menu.hide_with_anim()

    def on_timer_finished(self, menu) -> None:
        self.timer.stop()
        menu.show_with_anim()


class SideButton(QtWidgets.QPushButton):
    pixmap_name: str
    state: int = 0

    def __init__(self, pixmap_name: str, size: QtCore.QSize, f: Callable = None) -> None:
        super(SideButton, self).__init__()

        self.pixmap_name = pixmap_name
        self.setFixedSize(size)
        self.setIcon(QtGui.QPixmap(f':/img/{pixmap_name}.png'))
        self.setIconSize(size)
        self.icon_name = pixmap_name
        self.clicked.connect(f) if f else None
