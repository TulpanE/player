from PySide6 import QtWidgets, QtCore, QtGui
import settings
from src.client.tools.style_setter import set_style_sheet
from src.client.animated_panel import AnimatedPanel
from src.client.tools.config_manager import ConfigManager
from src.client.toggle_button import ToggleButton


class SettingsMenu(AnimatedPanel):
    def __init__(self, parent) -> None:
        super(SettingsMenu, self).__init__(parent)
        self.__init_ui()
        self.hide()

    def __init_ui(self) -> None:
        self.setObjectName("SettingsMenu")
        set_style_sheet(self, 'settings_menu.qss')

        self.general_settings: SettingsMenu.GeneralSettings = SettingsMenu.GeneralSettings()
        self.hitmo_integration: SettingsMenu.HitmoSettings = SettingsMenu.HitmoSettings()

        self.main_layout.addWidget(self.general_settings)
        self.main_layout.addItem(QtWidgets.QSpacerItem(0, 5, QtWidgets.QSizePolicy.Policy.Fixed))
        self.main_layout.addWidget(self.hitmo_integration)

        self.save_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        self.save_button.setObjectName("SaveButton")
        self.save_button.setText("Принять")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setParent(self)
        self.save_button.setMaximumSize(100, 30)
        self.save_button.move(self.parent().width() // 2 - 60, self.parent().height() - 110)

    def resizeEvent(self, event):
        self.save_button.move(self.parent().width() // 2 - 60, self.parent().height() - 110)

    def save_settings(self) -> None:
        config: dict = ConfigManager.get_config()
        config['music_dir'] = self.general_settings.music_dir_line_edit.text()
        config['hitmo_integration_include'] = self.hitmo_integration.include_hitmo_toggle_button.isChecked()
        config['download_on_play'] = self.hitmo_integration.download_on_play_toggle_button.isChecked()
        ConfigManager.update_config(config)
        self.parent().reload_panels()
        self.parent().side_menu.on_settings_pressed()

    def reload(self) -> None:
        config: dict = ConfigManager.get_config()
        self.general_settings.music_dir_line_edit.setText(config['music_dir'])
        self.hitmo_integration.include_hitmo_toggle_button.setChecked(config['hitmo_integration_include'])
        self.hitmo_integration.download_on_play_toggle_button.setChecked(config['download_on_play'])

    class SettingsPoint(QtWidgets.QFrame):
        title: str = 'Title'
        pixmap_path: str = ''

        def __init__(self, title, pixmap_path) -> None:
            super(SettingsMenu.SettingsPoint, self).__init__()
            self.title = title
            self.pixmap_path = pixmap_path
            self.__init_ui()

        def __init_ui(self) -> None:
            self.setObjectName("SettingsPoint")
            self.main_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
            self.title_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.title_layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.main_layout)
            self.main_layout.addLayout(self.title_layout)
            self.setMinimumHeight(50)
            self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.title_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            self.title_label: QtWidgets.QLabel = QtWidgets.QLabel(self.title)
            self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.title_label.setObjectName("TitleLayout")
            self.icon = QtWidgets.QLabel()
            self.icon.setPixmap(QtGui.QPixmap(self.pixmap_path))
            self.icon.setScaledContents(True)
            self.icon.setFixedSize(20, 20)

            self.title_layout.addWidget(self.icon)
            self.title_layout.addWidget(self.title_label)
            self.main_layout.addItem(QtWidgets.QSpacerItem(0, 15, QtWidgets.QSizePolicy.Policy.Fixed))

    class GeneralSettings(SettingsPoint):
        def __init__(self) -> None:
            super(SettingsMenu.GeneralSettings, self).__init__(
                title='Главное',
                pixmap_path=f':/img/settings_title.png'
            )
            self.__init_ui()

        def __init_ui(self) -> None:
            self.music_dir_select_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.music_dir_select_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.addLayout(self.music_dir_select_layout)

            self.music_dir_line_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
            self.search_button: QtWidgets.QPushButton = QtWidgets.QPushButton("...")

            self.music_dir_select_layout.addWidget(QtWidgets.QLabel("Папка с музыкой"))
            self.music_dir_select_layout.addWidget(self.music_dir_line_edit)
            self.music_dir_select_layout.addWidget(self.search_button)

            self.search_button.setFixedSize(20, 20)
            self.music_dir_line_edit.setFixedHeight(20)
            self.music_dir_line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            self.music_dir_line_edit.setEnabled(False)

            self.search_button.clicked.connect(self.show_folder_dialog)

        def show_folder_dialog(self) -> None:
            music_dir: str = QtWidgets.QFileDialog.getExistingDirectory(
                self, 'Выберите папку', QtCore.QDir.currentPath()
            )
            self.music_dir_line_edit.setText(music_dir)

    class HitmoSettings(SettingsPoint):
        def __init__(self) -> None:
            super(SettingsMenu.HitmoSettings, self).__init__(
                title='Hitmo-интеграция',
                pixmap_path=f':/img/hitmo_title.png'
            )
            self.__init_ui()

        def __init_ui(self) -> None:
            self.include_hitmo_toggle_button: ToggleButton = ToggleButton(width=40)
            self.include_hitmo_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.include_hitmo_layout)
            self.include_hitmo_layout.setContentsMargins(0, 0, 0, 0)

            self.include_hitmo_layout.addWidget(QtWidgets.QLabel('Включить интеграцию'))
            self.include_hitmo_layout.addItem(QtWidgets.QSpacerItem(10, 0))
            self.include_hitmo_layout.addWidget(self.include_hitmo_toggle_button)

            self.download_on_play_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.download_on_play_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.addLayout(self.download_on_play_layout)
            self.download_on_play_toggle_button: ToggleButton = ToggleButton(width=40)

            self.download_on_play_layout.addWidget(QtWidgets.QLabel('Загружать при проигрывании'))
            self.download_on_play_layout.addItem(QtWidgets.QSpacerItem(10, 0))
            self.download_on_play_layout.addWidget(self.download_on_play_toggle_button)

            self.main_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding))