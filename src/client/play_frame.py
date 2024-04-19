import os
import tempfile
from PySide6 import QtWidgets, QtGui, QtCore
import settings
from src.client.tools.style_setter import set_style_sheet
from src.client.tools.track_loader import get_tracks_in_music_dir
import pygame
import eyed3
from io import BytesIO
from random import randint
import requests
import threading
from src.client.tools.config_manager import ConfigManager


class PlayFrame(QtWidgets.QFrame):
    play_button_state: int = 1
    active_track: eyed3.AudioFile = None
    required_track_url: str = None

    def __init__(self) -> None:
        super(PlayFrame, self).__init__()
        pygame.mixer.init()
        self.__init_ui()
        self.toggle_play_button()

    def __init_ui(self):

        self.setObjectName("PlayFrame")

        set_style_sheet(self, 'play_frame.qss')

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 15, 5, 5)
        control_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        control_layout.setContentsMargins(0, 15, 0, 15)
        control_layout.setObjectName("ControlLayout")
        duration_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        duration_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

        control_widget: QtWidgets.QFrame = QtWidgets.QFrame()
        duration_widget: QtWidgets.QFrame = QtWidgets.QFrame()

        self.play_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        self.back_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        self.next_button: QtWidgets.QPushButton = QtWidgets.QPushButton()
        self.duration_bar: PlayFrame.DurationBar = PlayFrame.DurationBar(self)
        self.current_time_label: QtWidgets.QLabel = QtWidgets.QLabel()
        self.all_time_label: QtWidgets.QLabel = QtWidgets.QLabel()

        main_layout.addWidget(duration_widget)
        main_layout.addWidget(control_widget)
        control_widget.setLayout(control_layout)
        duration_widget.setLayout(duration_layout)

        control_layout.addWidget(self.back_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        duration_layout.addWidget(self.current_time_label)
        duration_layout.addWidget(self.duration_bar)
        duration_layout.addWidget(self.all_time_label)

        self.play_button.setFixedSize(35, 35)
        self.back_button.setFixedSize(30, 30)
        self.next_button.setFixedSize(30, 30)
        self.play_button.setIcon(QtGui.QPixmap(f':/img/play.png'))
        self.play_button.setIconSize(self.play_button.size())
        self.next_button.setIcon(QtGui.QPixmap(f':/img/next.png'))
        self.next_button.setIconSize(self.next_button.size())
        self.back_button.setIcon(
            QtGui.QPixmap(f':/img/next.png').transformed(QtGui.QTransform().scale(-1, 1))
        )
        self.back_button.setIconSize(self.back_button.size())
        self.current_time_label.setText('00:00')
        self.all_time_label.setText('00:00')

        control_widget.setObjectName("ControlWidget")
        duration_widget.setObjectName("DurationWidget")
        self.play_button.setObjectName("PlayButton")
        self.next_button.setObjectName("NextButton")
        self.back_button.setObjectName("BackButton")

        self.play_button.clicked.connect(self.on_play_clicked)
        self.next_button.pressed.connect(self.pressed_next_or_back_button)
        self.back_button.pressed.connect(self.pressed_next_or_back_button)
        self.next_button.released.connect(self.released_next_or_back_button)
        self.back_button.released.connect(self.released_next_or_back_button)

        timer: QtCore.QTimer = QtCore.QTimer(self)
        timer.timeout.connect(self.app_loop)
        timer.start(1)

    def set_track(self, track: eyed3.AudioFile) -> None:
        pygame.mixer.music.stop()
        self.active_track = track
        self.duration_bar.setMaximum(int(track.info.time_secs * 1000))

        if track.tag.images:
            pixmap: QtGui.QPixmap = QtGui.QPixmap()
            pixmap.loadFromData(BytesIO(track.tag.images[0].image_data).getvalue())
        else:
            pixmap: QtGui.QPixmap = QtGui.QPixmap(f':/img/track.png')

        self.parent().track_info.set_track_info(self.active_track, pixmap)
        self.duration_bar.start_pos = 0
        time_secs: int = int(self.active_track.info.time_secs)
        minutes: int = time_secs // 60
        seconds: int = time_secs % 60

        if minutes < 10:
            minutes: str = '0' + str(minutes)

        if seconds < 10:
            seconds: str = '0' + str(seconds)

        self.all_time_label.setText(f'{minutes}:{seconds}')
        pygame.mixer.music.load(self.active_track.path)
        pygame.mixer.music.play()

    def set_track_by_url(self, track_url: str) -> None:
        self.required_track_url = track_url

        threading.Thread(target=lambda: self.download_required_track(track_url)).start()

    def download_required_track(self, track_url: str) -> None:
        self.parent().track_info.load_indicator.show()
        self.parent().track_info.track_image.hide()
        self.parent().track_info.track_name.setText('Загрузка')

        track = requests.get(track_url).content

        if track_url != self.required_track_url or not threading.main_thread().is_alive():
            exit()

        temp_fd, temp_filename = tempfile.mkstemp(suffix=".mp3", prefix=settings.TEMPFILE_PREFIX)

        with os.fdopen(temp_fd, "wb") as temp_file:
            temp_file.write(track)

        download_on_play: bool = ConfigManager.get_config()['download_on_play']

        if download_on_play:
            new_file_path: str = f'{ConfigManager.get_config()['music_dir']}/{track_url.split('/')[-1]}'
            with open(new_file_path, 'wb') as audiofile:
                audiofile.write(track)

        loaded_track: eyed3.AudioFile = eyed3.load(temp_filename if not download_on_play else new_file_path)

        self.parent().track_info.load_indicator.hide()
        self.parent().track_info.track_image.show()

        self.set_track(loaded_track)

    @staticmethod
    def play() -> None:
        pygame.mixer.music.unpause()

    @staticmethod
    def pause() -> None:
        pygame.mixer.music.pause()

    @staticmethod
    def stop() -> None:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def change_track(self, next_track: bool = True) -> None:
        if self.active_track is None:
            return

        track_list: list = get_tracks_in_music_dir(True)
        active_track_position: int = -1

        for track in track_list:
            active_track_position += 1
            if track.path == self.active_track.path:
                break

        if next_track:
            active_track_position = 0 if active_track_position == len(track_list) - 1 else active_track_position + 1

        else:
            active_track_position = len(track_list) - 1 if active_track_position == 0 else active_track_position - 1

        self.set_track(track_list[active_track_position])

    def on_play_clicked(self) -> None:
        self.toggle_play_button()
        if self.active_track is None:
            return

        if self.play_button_state:
            self.play()
        else:
            self.pause()

    def toggle_play_button(self) -> None:
        self.play_button_state = not self.play_button_state
        state: str = 'play' if self.play_button_state else 'pause'
        self.play_button.setIcon(QtGui.QPixmap(f':/img/{state}.png'))

    def pressed_next_or_back_button(self) -> None:
        self.toggle_next_or_back_button(1)

        if self.sender().objectName() == 'NextButton':
            if self.parent().side_menu.randomize_button.state:
                self.set_track(self.get_random_track())
            else:
                self.change_track(True)
        else:
            self.change_track(False)

    def released_next_or_back_button(self):
        self.toggle_next_or_back_button(0)

    def toggle_next_or_back_button(self, state: int) -> None:
        icon_path: str = f':/img/next{"_pressed" if state else ""}.png'
        icon = QtGui.QPixmap(icon_path)

        if self.sender().objectName() == 'BackButton':
            icon = QtGui.QPixmap(icon_path).transformed(QtGui.QTransform().scale(-1, 1))

        self.sender().setIcon(icon)

    def app_loop(self) -> None:
        self.update_duration_bar()

        if self.active_track is not None:
            if (pygame.mixer.music.get_pos() == (
                    self.active_track.info.time_secs * 1000) - 200 - self.duration_bar.start_pos and
                    pygame.mixer.music.get_pos() != -1):
                self.track_ended_callback()

    def track_ended_callback(self) -> None:
        if self.parent().side_menu.repeat_button.state:
            self.change_track(True)
            self.change_track(False)

        elif self.parent().side_menu.randomize_button.state:
            self.set_track(self.get_random_track())

        else:
            self.change_track(True)

    def update_duration_bar(self) -> None:
        if not pygame.mixer.music.get_busy():
            return

        time_secs: int = (pygame.mixer.music.get_pos() + self.duration_bar.start_pos) // 1000
        minutes: int = time_secs // 60
        seconds: int = time_secs % 60

        if minutes < 10:
            minutes: str = '0' + str(minutes)

        if seconds < 10:
            seconds: str = '0' + str(seconds)

        self.current_time_label.setText(f'{minutes}:{seconds}')
        self.duration_bar.update_duration()

    def get_random_track(self) -> eyed3.AudioFile:
        tracks: list[eyed3.AudioFile] = get_tracks_in_music_dir(sort=True)

        [tracks.remove(track) if track.path == self.active_track.path else 0 == 0 for track in tracks]

        return tracks[randint(0, len(tracks) - 1)]

    class DurationBar(QtWidgets.QProgressBar):
        start_pos: int = 0

        def __init__(self, parent) -> None:
            super(PlayFrame.DurationBar, self).__init__(parent)
            self.init_ui()

        def init_ui(self) -> None:
            self.setObjectName('DurationBar')

            self.setValue(0)
            self.setFixedHeight(10)
            self.setTextVisible(False)

        def mousePressEvent(self, event) -> None:
            if not pygame.mixer.music.get_busy():
                return

            pos_percent_clicked: int = int(event.pos().x() / self.size().width() * 100) + 1
            order_duration: int = (self.maximum() // 100) * pos_percent_clicked // 1000
            self.start_pos = order_duration * 1000
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=order_duration)

        def update_duration(self) -> None:
            self.setValue(self.start_pos + pygame.mixer.music.get_pos())
