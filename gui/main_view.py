import folium
import io
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSignal


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Widok przeglądarki
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Na start pokazujemy mapę
        self.show_map()

    def show_map(self, lat=52.2297, lon=21.0122, zoom=6):
        """Generuje i wyświetla mapę w podanych współrzędnych"""
        # Tworzymy mapę w folium

        m = folium.Map(location=[lat, lon], zoom_start=zoom)

        # Dodaj obsługę kliknięcia prawym przyciskiem (dodanie markera)
        m.add_child(folium.LatLngPopup())  # Kliknięcie pokaże popup z lat/lon

        # Konwersja do HTML w pamięci
        data = io.BytesIO()
        m.save(data, close_file=False)

        # Wyświetlenie mapy w QWebEngineView
        self.web_view.setHtml(data.getvalue().decode())


