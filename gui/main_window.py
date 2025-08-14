from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from gui.sidebar import Sidebar
from gui.main_view import MainView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikacja fotografa przyrody")
        self.resize(1200, 800)


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        self.sidebar = Sidebar()
        self.main_view = MainView()

        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.main_view, 4)
