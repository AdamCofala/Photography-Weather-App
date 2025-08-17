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

        # After adding localization -> update sidebar:
        self.main_view.config_was_updated.connect(self.sidebar.update_list)

        # After clicking add loc in side bar -> show map:
        self.sidebar.add_location.connect(self.main_view.show_map)

        self.sidebar.choose_location.connect(self.main_view.show_stats)
