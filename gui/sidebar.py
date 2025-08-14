from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
import random

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.location_list = QListWidget()
        layout.addWidget(self.location_list)

        self.add_btn = QPushButton("Dodaj lokalizację")
        self.add_btn.clicked.connect(self.addLoc)

        self.remove_btn = QPushButton("Usuń lokalizację")
        self.remove_btn.clicked.connect(self.delLoc)
        self.remove_btn.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.add_btn)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

    def addLoc(self):
        self.location_list.addItem(f"Otwock \n {random.uniform(-90, 90):.2f}, {random.uniform(-90, 90):.2f}")

    def delLoc(self):
        self.location_list.takeItem(self.location_list.currentRow())