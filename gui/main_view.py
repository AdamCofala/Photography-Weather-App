from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Na razie placeholder
        self.label = QLabel("Tutaj będzie mapa lub statystyki")
        layout.addWidget(self.label)

        self.setLayout(layout)
