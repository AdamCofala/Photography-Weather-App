from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
import random
import logic.location_base as loc

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.location_list = QListWidget()
        layout.addWidget(self.location_list)
        self.update_list()

        self.add_btn = QPushButton("Dodaj lokalizację")
        self.add_btn.clicked.connect(self.add_loc)

        self.remove_btn = QPushButton("Usuń lokalizację")
        self.remove_btn.clicked.connect(self.remove_loc)
        self.remove_btn.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.add_btn)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

    def update_list(self):
        self.location_list.clear()
        locations = loc.get_locations("assets/config.json")
        if locations:
            for location in locations:
                self.location_list.addItem(f"{location["Name"]}\n {location["Lat"]:.2f}, {location["Lon"]:.2f} ")

    def add_loc(self):
        # SIGNAL to main window to execute main_view.show_map()
        pass

    def remove_loc(self):
        current = self.location_list.currentRow()
        self.location_list.takeItem(current)
        loc.remove_loc("assets/config.json", current)
        self.update_list()
