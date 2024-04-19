import os
import settings
import tempfile
from PySide6 import QtWidgets, QtCore, QtGui
from src.client.settings_menu import SettingsMenu
from src.client.play_frame import PlayFrame
from src.client.play_list_menu import PlayListMenu
from src.client.track_info import TrackInfo
from src.client.side_menu import SideMenu
from src.client.tools.style_setter import set_style_sheet


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle("Frequency")
        self.resize(350, 515)
        self.setMinimumWidth(250)
        self.setObjectName("MainWindow")
        self.setWindowIcon(QtGui.QIcon(':/img/app_icon.ico'))

        set_style_sheet(self, 'main_window.qss')

        main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

        self.track_info: TrackInfo = TrackInfo()
        self.play_frame: PlayFrame = PlayFrame()
        self.side_menu: SideMenu = SideMenu()
        self.settings_menu: SettingsMenu = SettingsMenu(self)
        self.play_list_menu: PlayListMenu = PlayListMenu(self)
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom)
        main_layout.addWidget(self.track_info)
        main_layout.addItem(QtWidgets.QSpacerItem(0, 5, QtWidgets.QSizePolicy.Policy.Fixed))
        main_layout.addWidget(self.play_frame)
        main_layout.addItem(QtWidgets.QSpacerItem(0, 5, QtWidgets.QSizePolicy.Policy.Fixed))
        main_layout.addWidget(self.side_menu)

        self.settings_menu.move(10, 10)
        self.settings_menu.raise_()
        self.play_list_menu.move(10, 10)
        self.play_list_menu.raise_()

    def closeEvent(self, event) -> None:
        self.play_frame.stop()
        for file in os.listdir(tempfile.gettempdir()):
            if file.startswith(settings.TEMPFILE_PREFIX):
                os.remove(tempfile.gettempdir() + '/' + file)

    def reload_panels(self) -> None:
        self.play_list_menu.reload()
        self.settings_menu.reload()

    def resizeEvent(self, event):
        self.settings_menu.size_expand()
        self.play_list_menu.size_expand()
        pass
