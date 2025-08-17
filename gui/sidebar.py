from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
import random
import logic.location_base as loc

class Sidebar(QWidget):

    add_location = pyqtSignal()
    choose_location = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.location_list = QListWidget()
        layout.addWidget(self.location_list)
        self.update_list()

       # If item was clicked send info to main and then show the stats!
        self.location_list.itemClicked.connect(self.choose_loc)

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
        self.location_list.setCurrentRow(-1)  # no current row
        self.location_list.clearSelection()  # no selected items
        self.add_location.emit()

    def choose_loc(self):
        self.choose_location.emit(self.location_list.currentRow())


    def remove_loc(self):
        current = self.location_list.currentRow()

        # Check if there's actually a valid item selected
        if current < 0 or current >= self.location_list.count():
            return  # No valid selection, don't remove anything

        # Remove from the JSON file
        loc.remove_loc("assets/config.json", current)

        # Get the count before updating
        old_count = self.location_list.count()

        # Update the list (this rebuilds from JSON)
        self.update_list()

        # Handle selection after removal
        new_count = self.location_list.count()
        if new_count == 0:
            return

        # Determine which row to select
        if current >= new_count:
            new_row = new_count - 1  # Select last item if we removed the last item
        else:
            new_row = current  # Select item that moved into this position

        # Set selection
        self.location_list.setCurrentRow(new_row)
        item = self.location_list.item(new_row)
        if item:
            item.setSelected(True)
            self.choose_location.emit(self.location_list.currentRow())

