from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, pyqtSignal
import tempfile, os, sys, json, re
import logic.utils.location_base as loc
import logic.utils.haversine as hv
from logic.map.map_handler import MapHandler


class MainView(QWidget):
    config_was_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.stats_active = False
        self.map_active = False
        self.map_handler = MapHandler()
        self.show_map()

    def show_stats(self, id):
        print(id)

    def show_map(self, lat=52.2297, lon=21.0122, zoom=6):

        if self.map_active:
            return 0

        self.map_active = True

        self.web_view = QWebEngineView()
        self.layout().addWidget(self.web_view)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_coordinates)
        self.timer.start(100)

        self.coords_file = tempfile.mktemp(suffix='.json')

        # Use MapHandler to create and save the map
        self.m = self.map_handler.create_map(lat, lon, zoom)
        temp_html = self.map_handler.save_map_to_temp_file()


        self.web_view.load(QUrl.fromLocalFile(temp_html))

    def check_coordinates(self):
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

    def process_coordinates(self, lat, lng, time):
        with open("assets/polish_cities.json", "r", encoding="utf-8") as f:
            cities = json.load(f)

        name = hv.find_closest(lat, lng, cities)["Name"]
        locaction = loc.Location(str(name), lat, lng, time, "assets/config.json").to_json()
        self.config_was_updated.emit()

    def close_map(self):
        self.layout().removeWidget(self.web_view)
        self.web_view.deleteLater()
        self.web_view = None
        self.map_active = False

    def cleanup_file(self, filepath):
        MapHandler.cleanup_file(filepath)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainView()
    window.show()

    sys.exit(app.exec_())