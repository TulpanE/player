from PySide6.QtWidgets import QApplication
from src.client.main_window import MainWindow


if __name__ == "__main__":
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    app.exec()
