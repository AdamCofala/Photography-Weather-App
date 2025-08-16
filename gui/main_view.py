from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl,  QObject, pyqtSlot
import folium
from folium import Element
import io, tempfile, os, sys, json, re
import logic.location_base as loc

class MainView(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.map_active = True
        self.stats_active = False

        self.show_map()

    def show_map(self, lat=52.2297, lon=21.0122, zoom=6):

        self.map_active = True

        # Widok przeglądarki
        self.web_view = QWebEngineView()
        self.layout().addWidget(self.web_view)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_coordinates)
        self.timer.start(100)

        self.coords_file = tempfile.mktemp(suffix='.json')
        self.m = folium.Map(location=[lat, lon], zoom_start=zoom)

        # Pop up!
        popup = folium.LatLngPopup()
        self.m.add_child(popup)

        # Zapisz do tymczasowego pliku HTML
        temp_html = tempfile.mktemp(suffix='.html')
        self.m.save(temp_html)

        # Wczytaj HTML
        with open(temp_html, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Edytuj funkcję latLngPop
        modified_html = self.modify_html(html_content)

        # Zapisz zmodyfikowany HTML
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)

        # Załaduj w przeglądarce
        self.web_view.load(QUrl.fromLocalFile(temp_html))

        # Wyczyść tymczasowy plik po załadowaniu
        QTimer.singleShot(2000, lambda: self.cleanup_file(temp_html))

    def modify_html(self, html_content):
        # Znajdź funkcję latLngPop
        pattern = r'function latLngPop\(e\)\s*\{[^}]+\}'

        style = """
        <style>
        /* Wszystkie elementy */
        * {
            cursor: default !important;
        }
        
        *:focus {
            outline: none;
        }

        /* Twoje przyciski w popupach */
        .custom-popup-btn {
            background-color: #1e1e1e; /* ciemny grafit zamiast czystej czerni */
            color: #ffffff;             /* jasny tekst */
            border: 2px solid #444;     /* delikatna ramka dla kontrastu */
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5); /* lekki cień */
            transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
            font-size: 16px !important
        }

        .custom-popup-btn:hover {
            background-color: #ffffff;  /* jasny na hover */
            color: #1e1e1e;             /* ciemny tekst na hover */
            transform: translateY(-1px); /* lekki efekt "unoszenia" */
        }

        /* Popupy Leaflet */
        .leaflet-popup-content-wrapper {
            background: #242729 !important;
            color: white !important;
        }
        .leaflet-popup-tip {
            background: #222 !important;
        }

        </style>

        """
        html_content = html_content.replace("</head>", style + "</head>")

        # Nowa funkcja
        with open("logic/custom latLngPop.js", "r", encoding="utf-8") as f:
            new_function = f.read()

        modified_html = re.sub(pattern, new_function, html_content)
        return modified_html

    def check_coordinates(self):
        """Sprawdza czy są nowe współrzędne w localStorage"""
        js_code = """
        (function() {
            var coords = localStorage.getItem('lastCoordinates');
            if (coords) {
                localStorage.removeItem('lastCoordinates'); // Usuń po odczytaniu
                return coords;
            }
            return null;
        })();
        """
        if self.map_active:
            self.web_view.page().runJavaScript(js_code, self.handle_coordinates)

    def handle_coordinates(self, result):
        """Obsłuż otrzymane współrzędne"""
        if result:
            try:
                coords = json.loads(result)
                lat = coords['lat']
                lng = coords['lng']
                timestamp = coords['timestamp']
                self.close_map()
                self.process_coordinates(lat, lng, timestamp)
            except json.JSONDecodeError:
                pass

    def close_map(self):
        self.layout().removeWidget(self.web_view)
        self.web_view.deleteLater()
        self.web_view = None
        self.map_active = False

    def process_coordinates(self, lat, lng, time):
        """Przetwórz współrzędne w Python"""
        print(f"Przetwarzam współrzędne: {lat}, {lng}")

        locaction = loc.Location("temp", lat, lng, time, "assets/config.json").to_json()
        # - zapisz do bazy danych
        # - wyślij do API
        # - zaktualizuj inne części UI

    def cleanup_file(self, filepath):
        try:
            os.unlink(filepath)
        except:
            print("unlink didnt work")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainView()
    window.show()

    sys.exit(app.exec_())