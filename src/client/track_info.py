from PySide6 import QtWidgets, QtGui, QtCore
from src.client.tools.style_setter import set_style_sheet
import settings
from eyed3 import AudioFile
from src.client.load_indicator import LoadIndicator


class TrackInfo(QtWidgets.QFrame):
    def __init__(self) -> None:
        super(TrackInfo, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setObjectName("TrackInfo")
        set_style_sheet(self, 'track_info.qss')
        self.setFixedHeight(60)

        main_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        self.track_image: QtWidgets.QLabel = QtWidgets.QLabel()
        self.track_name: QtWidgets.QLabel = QtWidgets.QLabel()
        self.load_indicator: LoadIndicator = LoadIndicator(parent=self, radius_min=5, radius_max=12)
        self.load_indicator.setFixedWidth(50)

        self.load_indicator.hide()

        self.track_image.setObjectName("TrackImage")
        self.track_name.setObjectName("TrackName")

        self.track_name.setText("Ничего не играет")
        self.track_image.setFixedSize(45, 45)
        self.track_image.setPixmap(QtGui.QPixmap(f':/img/track.png'))
        self.track_image.setScaledContents(True)
        self.track_name.setContentsMargins(10, 0, 0, 0)

        main_layout.addWidget(self.track_image)
        main_layout.addWidget(self.load_indicator)
        main_layout.addWidget(self.track_name)

    def set_track_info(self, track: AudioFile, pixmap: QtGui.QPixmap) -> None:
        self.track_name.setText(f'{track.tag.title} • {track.tag.artist}')
        self.track_image.setPixmap(pixmap)
