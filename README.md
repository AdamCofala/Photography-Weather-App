# Nature Photography Weather App 📸🌦️

A PyQt5-based desktop application designed for nature photographers to track weather conditions and water levels at their favorite shooting locations across Poland.

## 🎯 Features

- **Interactive Map**: Click-to-add locations using Folium maps with custom styling
- **Weather Forecasting**: 48-hour detailed weather charts with temperature, precipitation, and cloud coverage
- **Hydrological Data**: Real-time water level monitoring from Polish hydrological stations
- **Location Management**: Save, view, and remove photography locations
- **Dark Theme**: Professional dark UI optimized for outdoor photographers
- **Sunrise/Sunset Times**: Visual markers for golden hour photography planning

## 📱 Screenshots

### Main Interface
*[Screenshot of the main window with sidebar and map view]*

### Weather Charts
*[Screenshot showing the detailed weather forecast charts]*

### Location Management
*[Screenshot of the sidebar with saved locations]*

### Interactive Map
*[Screenshot of the map interface with location markers]*

## 🏗️ Application Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   main.py       │────│ MainWindow       │────│   MainView      │
│                 │    │ (gui/main_       │    │ (gui/main_      │
│ - Entry point   │    │  window.py)      │    │  view.py)       │
│ - App styling   │    │                  │    │                 │
└─────────────────┘    │ - Window setup   │    │ - Map display   │
                       │ - Layout mgmt    │    │ - Stats display │
                       └─────────┬────────┘    │ - View switching│
                                 │             └─────────┬───────┘
                                 │                       │
                       ┌─────────▼────────┐             │
                       │   Sidebar        │             │
                       │ (gui/sidebar.py) │             │
                       │                  │             │
                       │ - Location list  │◄────────────┤
                       │ - Add/Remove     │             │
                       │ - Selection mgmt │             │
                       └─────────┬────────┘             │
                                 │                      │
        ┌────────────────────────┼──────────────────────┼────────────────┐
        │                        │                      │                │
┌───────▼────────┐    ┌─────────▼──────────┐    ┌──────▼─────────┐      │
│  MapHandler    │    │  Location Base     │    │ Chart Builder  │      │
│ (logic/map/    │    │ (logic/utils/      │    │ (logic/stats/  │      │
│  map_handler.  │    │  location_base.py) │    │  chart_builder │      │
│  py)           │    │                    │    │  .py)          │      │
│                │    │ - JSON storage     │    │                │      │
│ - Folium maps  │    │ - Location class   │    │ - MeteoPlot    │      │
│ - Custom JS    │    │ - CRUD operations  │    │ - HydroPlot    │      │
│ - HTML styling │    └─────────┬──────────┘    │ - Matplotlib   │      │
└───────┬────────┘              │               └──────┬─────────┘      │
        │                       │                      │                │
        │              ┌────────▼───────────┐          │                │
        │              │   Haversine        │          │                │
        │              │ (logic/utils/      │          │                │
        │              │  haversine.py)     │          │                │
        │              │                    │          │                │
        │              │ - Distance calc    │          │                │
        │              │ - Closest city     │          │                │
        │              │ - Closest station  │          │                │
        │              └────────────────────┘          │                │
        │                                              │                │
        └──────────────────────────┬─────────────────────────────────────┘
                                   │
                         ┌─────────▼──────────┐
                         │   Data Fetcher     │
                         │ (logic/stats/      │
                         │  data_fetcher.py)  │
                         │                    │
                         │ - Weather API      │
                         │ - Sun times API    │
                         │ - Hydro data API   │
                         │ - Data processing  │
                         └────────────────────┘
```

## 📁 Project Structure

```
nature_photo_app/
├── main.py                          # Application entry point
├── assets/
│   ├── config.json                  # Saved locations data
│   ├── polish_cities.json           # Polish cities database
│   └── dark.qss                     # Dark theme stylesheet
├── gui/
│   ├── main_window.py               # Main application window
│   ├── main_view.py                 # Central display area controller
│   └── sidebar.py                   # Location management sidebar
└── logic/
    ├── map/
    │   ├── map_handler.py           # Folium map management
    │   └── custom latLngPop.js      # Custom JavaScript for map interactions
    ├── stats/
    │   ├── chart_builder.py         # Weather and hydro chart generation
    │   └── data_fetcher.py          # API data retrieval and processing
    └── utils/
        ├── location_base.py         # Location data management
        └── haversine.py             # Geographic distance calculations
```

## 🔄 Application Flow

### 1. **Startup**
- `main.py` initializes PyQt5 application
- Dark theme stylesheet is applied
- `MainWindow` creates the main interface with sidebar and view area

### 2. **Location Management**
- **Adding Locations**: 
  - User clicks "Dodaj lokalizację" → Map view opens
  - User clicks on map → Coordinates are captured via JavaScript
  - Closest Polish city is found using Haversine distance
  - Location is saved to `config.json` and added to sidebar

- **Viewing Statistics**: 
  - User selects location from sidebar
  - Weather and hydrological data is fetched from APIs
  - Charts are generated and displayed in the main view

### 3. **Data Flow**
```
User Selection → Data Fetcher → API Requests → Chart Builder → Display
     ↓              ↓              ↓              ↓           ↓
   Location      Coordinates    Weather &      Matplotlib   PyQt5
   from JSON      to APIs      Hydro Data      Charts      Widgets
```

## 🛠️ Technical Implementation

### **GUI Architecture**
- **PyQt5 Framework**: Modern desktop GUI with native OS integration
- **Signal-Slot Pattern**: Clean communication between components
- **Dynamic View Switching**: Seamless transitions between map and chart views
- **Resource Management**: Proper cleanup of widgets and temporary files

### **Weather Data Visualization**
- **Matplotlib Integration**: Professional-grade charts with dark theme
- **48-Hour Forecasting**: Temperature, precipitation, cloud cover, and day/night cycles
- **Smooth Interpolation**: Cubic spline interpolation for professional appearance
- **Multi-axis Charts**: Temperature, precipitation, and cloud cover on synchronized axes
- **Sunrise/Sunset Markers**: Visual indicators for golden hour photography

### **Map Integration**
- **Folium Maps**: Interactive OpenStreetMap-based mapping
- **Custom JavaScript**: Click-to-coordinates functionality with localStorage
- **Responsive UI**: Real-time coordinate capture and processing
- **Location Markers**: Visual indicators for saved photography locations

### **Data Sources**
- **Open-Meteo API**: European weather forecasting data
- **Sunrise-Sunset API**: Astronomical data for photography planning  
- **Polish Hydrological Data**: Real-time water levels from GitHub repository
- **Geographic Calculations**: Haversine formula for distance calculations

## 📋 Requirements

### Dependencies
```
PyQt5>=5.15.0
matplotlib>=3.5.0
folium>=0.12.0
requests>=2.28.0
scipy>=1.9.0
numpy>=1.21.0
```

### System Requirements
- Python 3.8 or higher
- Qt5 WebEngine support
- Internet connection for API data and map tiles

## 🚀 Installation & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nature-photo-weather-app.git
   cd nature-photo-weather-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Usage**
   - Click "Dodaj lokalizację" to add new photography locations
   - Select locations from the sidebar to view weather and water level data
   - Plan your photography sessions using the 48-hour weather forecasts
   - Monitor water levels for landscape and wildlife photography

## 🎨 Features in Detail

### Weather Charts
- **Temperature Trends**: Actual and "feels like" temperature with smooth curves
- **Precipitation Forecast**: Hourly rainfall predictions with value labels
- **Cloud Coverage**: Percentage cloud cover for lighting conditions
- **Day/Night Cycles**: Visual background indicating daylight hours
- **Professional Styling**: Dark theme optimized for outdoor photographers

### Hydrological Monitoring
- **Real-time Data**: Current water levels from Polish monitoring stations
- **Closest Station**: Automatic selection of nearest monitoring point
- **Historical Trends**: Recent water level changes for planning
- **Smooth Visualization**: Interpolated curves for professional presentation

### Location Intelligence
- **Geographic Accuracy**: Precise coordinate capture and city identification
- **Distance Calculations**: Haversine formula for accurate geographic distances
- **Persistent Storage**: JSON-based location database with ID management
- **Smart Selection**: Automatic selection of closest cities and monitoring stations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Open-Meteo**: For providing free weather API access
- **Polish Hydrological Data**: For real-time water level monitoring
- **OpenStreetMap**: For map tiles and geographic data
- **PyQt5**: For the robust desktop GUI framework

---

**Perfect for nature photographers who want to:**
- 🌅 Plan golden hour sessions with sunrise/sunset data
- 🌦️ Avoid bad weather with accurate forecasting
- 🏞️ Monitor water levels for landscape photography
- 📍 Organize and revisit favorite shooting locations
- 📊 Make data-driven decisions for outdoor photography
