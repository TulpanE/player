import settings
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
import src.client.resources_rc


def set_style_sheet(widget: QWidget, file: str):
    style_file: QFile = QFile(f':/style/{file}')
    
    if style_file.open(QFile.ReadOnly | QFile.Text):
        widget.setStyleSheet(style_file.readAll().data().decode("utf-8"))
