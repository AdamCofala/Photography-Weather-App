from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QGridLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl, pyqtSignal, Qt
import tempfile, sys, json
import logic.utils.location_base as loc
import logic.utils.haversine as hv
from logic.map.map_handler import MapHandler
import logic.stats.chart_builder as cb




class MainView(QWidget):
    config_was_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.stats_active = False
        self.map_active = False
        self.map_handler = MapHandler()

        # Initialize all widgets as None
        self.meteo_view = None
        self.hydro_view = None
        self.web_view = None
        self.timer = None
        self.coords_file = None
        self.m = None

        self.show_map()

    def show_stats(self, id):
        # Clean up existing views first
        self._cleanup_all_views()

        # Set state and create stats view
        self.stats_active = True
        self.map_active = False

        try:
            # Create meteo plot
            meteo_plot = cb.MeteoPlot(id)
            self.meteo_view = meteo_plot.canvas if hasattr(meteo_plot, 'canvas') else meteo_plot
            self.meteo_view.setObjectName("meteo_chart")

            self.layout().addWidget(self.meteo_view)

            hydro_plot = cb.HydroPlot(id)
            self.hydro_view = hydro_plot.canvas if hasattr(hydro_plot, 'canvas') else hydro_plot
            self.hydro_view.setObjectName("hydro_chart")

            self.layout().addWidget(self.hydro_view)

        except Exception as e:
            print(f"Error creating stats view: {e}")
            self.stats_active = False

    def show_map(self, lat=52.2297, lon=21.0122, zoom=6):
        # Don't recreate if map is already active with same parameters
        if self.map_active:
            return

        # Clean up existing views first
        self._cleanup_all_views()

        # Set state and create map view
        self.map_active = True
        self.stats_active = False

        try:
            # Create web view
            self.web_view = QWebEngineView()
            self.layout().addWidget(self.web_view)

            # Setup coordinate checking timer
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_coordinates)
            self.timer.start(100)

            # Create temporary file for coordinates
            self.coords_file = tempfile.mktemp(suffix='.json')

            # Use MapHandler to create and save the map
            self.m = self.map_handler.create_map(lat, lon, zoom)
            temp_html = self.map_handler.save_map_to_temp_file()

            # Load the map
            self.web_view.load(QUrl.fromLocalFile(temp_html))

        except Exception as e:
            print(f"Error creating map view: {e}")
            self.map_active = False

    def check_coordinates(self):
        if not self.map_active or not self.web_view:
            return

        js_code = """
        (function() {
            var coords = localStorage.getItem('lastCoordinates');
            if (coords) {
                localStorage.removeItem('lastCoordinates'); // Remove after reading
                return coords;
            }
            return null;
        })();
        """

        try:
            self.web_view.page().runJavaScript(js_code, self.handle_coordinates)
        except Exception as e:
            print(f"Error checking coordinates: {e}")

    def handle_coordinates(self, result):
        if not result:
            return

        try:
            coords = json.loads(result)
            lat = coords.get('lat')
            lng = coords.get('lng')
            timestamp = coords.get('timestamp')

            if lat is not None and lng is not None:
                # Process coordinates and close map
                self.process_coordinates(lat, lng, timestamp)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error parsing coordinates: {e}")

    def process_coordinates(self, lat, lng, time):
        try:
            with open("assets/polish_cities.json", "r", encoding="utf-8") as f:
                cities = json.load(f)

            closest_city = hv.find_closest_city(lat, lng, cities)
            name = closest_city.get("Name", "Unknown")

            # Create location and save to config
            location = loc.Location(str(name), lat, lng, time, "assets/config.json")
            location.to_json()

            # Emit signal that config was updated
            self.config_was_updated.emit()

            # Close map after processing
            self.close_map()

        except Exception as e:
            print(f"Error processing coordinates: {e}")

    def _cleanup_all_views(self):
        """Clean up all active views"""
        if self.map_active:
            self.close_map()
        if self.stats_active:
            self.close_stats()

    def close_map(self):
        if not self.map_active:
            return

        # Stop and clean up timer
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

        # Clean up web view
        if self.web_view:
            self.layout().removeWidget(self.web_view)
            self.web_view.deleteLater()
            self.web_view = None

        # Clean up temporary files
        if self.coords_file:
            self.cleanup_file(self.coords_file)
            self.coords_file = None

        # Reset map reference
        self.m = None
        self.map_active = False

    def close_stats(self):
        if not self.stats_active:
            return

        # Clean up meteo view
        if self.meteo_view:
            self.layout().removeWidget(self.meteo_view)
            self.meteo_view.deleteLater()
            self.meteo_view = None

        if self.hydro_view:
            self.layout().removeWidget(self.hydro_view)
            self.hydro_view.deleteLater()
            self.hydro_view = None

        self.stats_active = False

    def cleanup_file(self, filepath):
        try:
            MapHandler.cleanup_file(filepath)
        except Exception as e:
            print(f"Error cleaning up file {filepath}: {e}")

    def closeEvent(self, event):
        """Clean up resources when window is closed"""
        try:
            self._cleanup_all_views()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainView()
    window.show()

    sys.exit(app.exec_())