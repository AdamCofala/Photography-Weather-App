import folium
import tempfile
import os
import re
import logic.utils.location_base as loc

class MapHandler:
    def __init__(self):
        self.m = None

    def create_map(self, lat=52.2297, lon=21.0122, zoom=6):
        """Create a folium map with popup and markers"""
        self.m = folium.Map(location=[lat, lon], zoom_start=zoom)

        # Pop up!
        popup = folium.LatLngPopup()
        self.m.add_child(popup)

        # Add existing location markers
        markers = loc.get_locations("assets/config.json")
        icon = folium.Icon(color="darkpurple", icon_color="white", icon="heart")

        for marker in markers:
            folium.Marker(location=[marker["Lat"], marker["Lon"]], icon=icon).add_to(self.m)

        return self.m

    def save_map_to_temp_file(self):
        """Save map to temporary HTML file with modifications"""
        temp_html = tempfile.mktemp(suffix='.html')
        self.m.save(temp_html)

        with open(temp_html, 'r', encoding='utf-8') as f:
            html_content = f.read()

        modified_html = self.modify_html(html_content)

        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)

        return temp_html

    def modify_html(self, html_content):
        """Modify HTML content with custom styling and JavaScript"""
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
        with open("logic/map/custom latLngPop.js", "r", encoding="utf-8") as f:
            new_function = f.read()

        modified_html = re.sub(pattern, new_function, html_content)
        return modified_html

    @staticmethod
    def cleanup_file(filepath):
        """Clean up temporary file"""
        try:
            os.unlink(filepath)
        except:
            return 0