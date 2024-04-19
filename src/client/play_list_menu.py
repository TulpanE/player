import eyed3
import requests
from PySide6 import QtWidgets, QtCore, QtGui
import settings
from src.client.tools.style_setter import set_style_sheet
from src.client.tools.config_manager import ConfigManager
from src.client.animated_panel import AnimatedPanel
from src.client.tools.track_loader import get_tracks_in_music_dir
from src.client.tools.hitmo_parser import find_tracks
from io import BytesIO
from src.client.toggle_button import ToggleButton
import threading
import os
import tempfile
from src.client.load_indicator import LoadIndicator


class PlayListMenu(AnimatedPanel):
    tracks: list = []

    def __init__(self, parent) -> None:
        super(PlayListMenu, self).__init__(parent)
        self.__init_ui()
        self.hide()

    def __init_ui(self) -> None:
        self.setObjectName("PlayListMenu")
        set_style_sheet(self, 'play_list_menu.qss')
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        if ConfigManager.get_config()['music_dir'] == '':
            self.set_notification('Похоже, папка с музыкой не указана')
            return

        scroll_area: QtWidgets.QScrollArea = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.verticalScrollBar().setMaximumWidth(6)
        scroll_area.verticalScrollBar().setObjectName('ScrollBar')
        scroll_area.setObjectName('ScrollArea')

        scroll_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        scroll_widget.setObjectName('ScrollWidget')
        self.scroll_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        scroll_widget.setLayout(self.scroll_layout)

        scroll_area.setWidget(scroll_widget)

        self.main_layout.addWidget(scroll_area)

        self.search_widget: PlayListMenu.SearchWidget = PlayListMenu.SearchWidget()
        self.main_layout.addWidget(self.search_widget)

        self.load_music()

    def set_notification(self, message: str) -> None:
        title: QtWidgets.QLabel = QtWidgets.QLabel()
        title.setText(message)
        title.setObjectName("TitleLabel")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addItem(QtWidgets.QSpacerItem(0, self.width() // 2, QtWidgets.QSizePolicy.Policy.Expanding,
                                                       QtWidgets.QSizePolicy.Policy.Expanding))
        self.main_layout.addWidget(title)
        self.main_layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Policy.Fixed))
        button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        button.setText('Настройки')
        self.main_layout.addWidget(button)
        button.clicked.connect(self.set_music_dir)
        button.setObjectName('ToSettingsButton')
        button.setMinimumSize(250, 30)
        self.main_layout.addItem(
            QtWidgets.QSpacerItem(0, self.width() // 2 + 40, QtWidgets.QSizePolicy.Policy.Expanding,
                                  QtWidgets.QSizePolicy.Policy.Expanding))

    def reload(self, only_clear: bool = False) -> None:
        layout = self.main_layout
        self.tracks.clear()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        if not only_clear:
            self.__init_ui()

    def set_music_dir(self) -> None:
        self.parent().side_menu.on_settings_pressed()

    def clear_tracks(self) -> None:
        for track in self.tracks:
            track.close()

        self.tracks.clear()

        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if isinstance(item, QtWidgets.QSpacerItem):
                self.scroll_layout.removeItem(item)

    def load_track(self,
                   track_info: list[str, str, str, str, str] = None,
                   track: eyed3.AudioFile = None,
                   ) -> None:

        if track:
            new_track_frame: PlayListMenu.TrackFrame = PlayListMenu.TrackFrame(track=track)
        else:
            new_track_frame: PlayListMenu.TrackFrame = PlayListMenu.TrackFrame(
                title=track_info[0],
                artist=track_info[1],
                album=track_info[2],
                pixmap_path=track_info[3],
                track_url=track_info[4]
            )

        self.scroll_layout.addWidget(new_track_frame)
        new_track_frame.size_expand()
        self.tracks.append(new_track_frame)

    def load_music(self) -> None:
        files: list = get_tracks_in_music_dir(True)

        if not files and not ConfigManager.get_config()['hitmo_integration_include']:
            self.set_notification('Тут как-то тихо..')
            self.search_widget.hide()
            return

        self.tracks.clear()

        for track in files:
            self.load_track(track=track)

    def size_expand(self) -> None:
        self.resize(self.parent().width() - 20, self.parent().height() - 70)
        for track in self.tracks:
            track.size_expand()

    class SearchWidget(QtWidgets.QFrame):
        required_track: str = ''
        track_added_signal: QtCore.Signal = QtCore.Signal(eyed3.AudioFile)
        move_load_indicator_signal: QtCore.Signal = QtCore.Signal()

        def __init__(self) -> None:
            super(PlayListMenu.SearchWidget, self).__init__()
            self.__init_ui()

        def __init_ui(self) -> None:
            self.setObjectName("SearchWidget")
            self.main_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.setLayout(self.main_layout)

            self.search_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
            self.search_button.setIcon(QtGui.QPixmap(f':/img/search.png'))
            self.search_button.enterEvent = self.mouse_enter_event
            self.search_button.leaveEvent = self.mouse_leave_event

            self.search_line_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
            self.search_line_edit.setFixedHeight(20)
            self.search_line_edit.textChanged.connect(self.on_search_line_edit_changed)

            self.main_layout.addWidget(self.search_button)
            self.main_layout.addWidget(self.search_line_edit)

            self.search_settings: QtWidgets.QFrame = QtWidgets.QFrame()

            self.search_settings.setObjectName('SearchSettings')
            self.search_settings_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
            self.search_settings_layout.setContentsMargins(5, 5, 5, 5)
            self.search_settings.setLayout(self.search_settings_layout)
            self.search_settings.setFixedSize(170, 70)
            self.search_settings.enterEvent = self.search_widget_mouse_enter_event
            self.search_settings.leaveEvent = self.search_widget_mouse_leave_event

            local_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            hitmo_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()

            local_layout.setContentsMargins(0, 0, 0, 0)
            hitmo_layout.setContentsMargins(0, 0, 0, 0)

            self.search_settings_layout.addLayout(local_layout)
            self.search_settings_layout.addLayout(hitmo_layout)

            self.local_search_toggle_button: ToggleButton = ToggleButton(width=40)
            self.hitmo_search_toggle_button: ToggleButton = ToggleButton(width=40)
            self.local_search_toggle_button.setEnabled(False)

            self.local_search_toggle_button.setChecked(ConfigManager.get_config()['local_search'])
            self.hitmo_search_toggle_button.setChecked(ConfigManager.get_config()['hitmo_integration_include'])

            self.hitmo_search_toggle_button.clicked.connect(self.on_toggle_button_pressed)

            local_layout.addWidget(self.local_search_toggle_button)
            local_layout.addWidget(QtWidgets.QLabel('Локальный поиск'))
            hitmo_layout.addWidget(self.hitmo_search_toggle_button)
            hitmo_layout.addWidget(QtWidgets.QLabel('Поиск в hitmo'))

            self.timer: QtCore.QTimer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.search_settings.hide)

            self.edit_timer: QtCore.QTimer = QtCore.QTimer(self)
            self.edit_timer.timeout.connect(self.on_search_line_edit_changed_end)

            self.track_added_signal.connect(self.track_add_slot)

        @QtCore.Slot(list)
        def track_add_slot(self, track_info: list[str, str, str, str, str]) -> None:
            self.parent().load_track(track_info=track_info)

        def on_toggle_button_pressed(self) -> None:
            if not ConfigManager.get_config()['hitmo_integration_include']:
                self.hitmo_search_toggle_button.setChecked(False)
                QtWidgets.QToolTip.showText(
                    self.mapToGlobal(
                        QtCore.QPoint(1, -80)
                    ),
                    'Сначала необходимо включить интеграцию в настройках')

        def on_search_line_edit_changed_end(self) -> None:
            self.edit_timer.stop()
            self.parent().clear_tracks()

            if self.search_line_edit.text() == '':
                self.parent().load_music()
                return

            if get_tracks_in_music_dir() or not self.hitmo_search_toggle_button.isChecked():
                label_section: PlayListMenu.LabelSection = PlayListMenu.LabelSection(title='Локальный поиск')
                self.parent().tracks.append(label_section)
                self.parent().scroll_layout.addWidget(label_section)
                self.parent().scroll_layout.addItem(QtWidgets.QSpacerItem(0, 5))

            for track in get_tracks_in_music_dir():
                if self.search_line_edit.text().lower() in track.tag.title.lower():
                    self.parent().load_track(track=track)

            if not self.hitmo_search_toggle_button.isChecked():
                return

            self.parent().scroll_layout.addItem(QtWidgets.QSpacerItem(0, 5))
            label_section: PlayListMenu.LabelSection = PlayListMenu.LabelSection(title='Hitmo')
            load_indicator: LoadIndicator = LoadIndicator(parent=self, radius_max=13, radius_min=4)
            self.parent().tracks.append(label_section)
            self.parent().tracks.append(load_indicator)
            self.parent().scroll_layout.addWidget(label_section)
            self.parent().scroll_layout.addItem(QtWidgets.QSpacerItem(0, 5))
            self.parent().scroll_layout.addWidget(load_indicator)

            threading.Thread(target=lambda: self.find_tracks_in_hitmo(self.required_track)).start()

        def find_tracks_in_hitmo(self, track_title: str) -> None:
            result: list[dict[str, str]] = find_tracks(track_title)

            for track in result:
                if self.required_track != track_title or not threading.main_thread().is_alive():
                    exit()

                audio_picture = requests.get(track['picture_url']).content
                temp_fd, temp_filename = tempfile.mkstemp(suffix=".png", prefix=settings.TEMPFILE_PREFIX)

                with os.fdopen(temp_fd, "wb") as temp_file:
                    temp_file.write(audio_picture)

                try:
                    self.track_added_signal.emit([
                        track['title'],
                        track['author'],
                        'Unknown',
                        temp_filename,
                        track['url_down']
                    ])
                except RuntimeError:
                    exit()

            try:
                for track in self.parent().tracks:
                    if isinstance(track, LoadIndicator):
                        track.close()
            except RuntimeError:
                exit()

        def on_search_line_edit_changed(self) -> None:
            self.edit_timer.stop()
            self.edit_timer.start(1000)
            self.required_track = self.search_line_edit.text()

        def search_widget_mouse_enter_event(self, event: QtCore.QEvent) -> None:
            self.timer.stop()

        def search_widget_mouse_leave_event(self, event: QtCore.QEvent) -> None:
            self.timer.start(500)

        def mouse_enter_event(self, event: QtCore.QEvent) -> None:
            if not self.search_settings.parent():
                self.search_settings.setParent(self.parent())

            self.search_settings.move(10, self.parent().size().height() - 120)
            self.timer.stop()
            self.search_settings.show()

        def mouse_leave_event(self, event: QtCore.QEvent) -> None:
            self.timer.start(500)

    class LabelSection(QtWidgets.QFrame):
        def __init__(self, title) -> None:
            super(PlayListMenu.LabelSection, self).__init__()

            self.title: str = title
            self.__init_ui()

        def __init_ui(self) -> None:
            self.setObjectName('LabelSection')
            self.setFixedHeight(23)

            layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label: QtWidgets.QWidget = QtWidgets.QLabel(self.title)

            self.setLayout(layout)

            layout.addWidget(label)

        def size_expand(self) -> None:
            self.setFixedWidth(self.parent().parent().parent().parent().width() - 20)

    class TrackFrame(QtWidgets.QFrame):
        track: eyed3.AudioFile
        title: str = 'Unknown'
        artist: str = 'Unknown'
        album: str = 'Unknown'
        pixmap_path: str = f':/img/track.png'
        track_url: str = None

        def __init__(self,
                     track: eyed3.AudioFile = None,
                     title: str = 'Unknown',
                     artist: str = 'Unknown',
                     album: str = 'Unknown',
                     pixmap_path: str = f':/img/track.png',
                     track_url: str = None
                     ) -> None:
            super(PlayListMenu.TrackFrame, self).__init__()

            if track:
                self.title = track.tag.title
                self.artist = track.tag.artist
                self.album = track.tag.album

            else:
                self.title = title
                self.artist = artist
                self.album = album
                self.track_url = track_url

            self.pixmap_path = pixmap_path
            self.track = track

            self.__init_ui()

        def __init_ui(self) -> None:
            self.setObjectName("TrackFrame")
            self.main_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
            self.setLayout(self.main_layout)
            self.setFixedHeight(40)

            label_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()

            self.pixmap_label: QtWidgets.QLabel = QtWidgets.QLabel()
            self.track_name_label: QtWidgets.QLabel = QtWidgets.QLabel()
            self.info_label: QtWidgets.QLabel = QtWidgets.QLabel()

            self.pixmap_label.setScaledContents(True)
            self.pixmap_label.setFixedSize(30, 30)
            self.pixmap_label.setObjectName('PixmapLabel')

            self.track_name_label.setText(self.title)
            self.info_label.setText(f'{self.artist} • {self.album}')
            self.info_label.setObjectName('InfoLabel')

            self.main_layout.addWidget(self.pixmap_label)
            self.main_layout.addItem(QtWidgets.QSpacerItem(5, 0, QtWidgets.QSizePolicy.Policy.Fixed))
            self.main_layout.addLayout(label_layout)

            label_layout.addWidget(self.track_name_label)
            label_layout.addWidget(self.info_label)

            if self.track and self.track.tag.images:
                pixmap: QtGui.QPixmap = QtGui.QPixmap()
                pixmap.loadFromData(BytesIO(self.track.tag.images[0].image_data).getvalue())
                self.pixmap_label.setPixmap(pixmap)

            else:
                self.pixmap_label.setPixmap(QtGui.QPixmap(self.pixmap_path))

        def mousePressEvent(self, event) -> None:
            self.setStyleSheet('background-color: rgb(60, 60, 60)')
            main_window = self.parent().parent().parent().parent().parent()
            main_window.side_menu.on_play_list_pressed()

            main_window.play_frame.set_track_by_url(self.track_url) if not self.track else (main_window.play_frame.
                                                                                            set_track(self.track))

            if not main_window.play_frame.play_button_state:
                main_window.play_frame.toggle_play_button()

        def mouseReleaseEvent(self, event) -> None:
            self.setStyleSheet('''
            QFrame#TrackFrame{background-color: rgb(70, 70, 70);} 
            QFrame#TrackFrame::hover{background-color: rgb(75, 75, 75);}
            ''')

        def size_expand(self) -> None:
            self.setFixedWidth(self.parent().parent().parent().parent().width() - 20)
