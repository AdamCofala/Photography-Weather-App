from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import logic.stats.data_fetcher as data_fetcher
from datetime import datetime, timedelta
import matplotlib as mpl
import numpy as np
from scipy.interpolate import interp1d


class MeteoPlot(FigureCanvas):
    """Weather forecast plot with temperature, precipitation, cloud cover, and sun markers."""

    def __init__(self, id, parent=None):
        super().__init__(parent)

        # Constants
        self.CHART_HOURS = 48
        self.MAIN_COLOR = '#ff4f64'
        self.APPARENT_COLOR = '#5bc0ff'
        self.RAIN_COLOR = '#4da6ff'
        self.CLOUD_COLOR = '#888888'
        self.SUNSET_COLOR = '#ff6b35'
        self.SUNRISE_COLOR = '#ffb347'

        # Initialize data and create plot
        self.id = id
        self._setup_matplotlib_style()
        if self._load_data():
            self._create_plot()

    def _setup_matplotlib_style(self):
        """Configure matplotlib style for dark theme."""
        mpl.rcParams.update({
            'figure.facecolor': '#1a1c1e',
            'axes.facecolor': '#1a1c1e',
            'axes.edgecolor': '#4a4f55',
            'axes.labelcolor': '#e0e0e0',
            'xtick.color': '#b0b0b0',
            'ytick.color': '#b0b0b0',
            'grid.color': '#3a3f45',
            'grid.linestyle': '--',
            'grid.alpha': 0.7,
            'lines.linewidth': 2.5,
            'font.size': 9,
            'font.family': 'Segoe UI',
            'legend.facecolor': '#2a2e32',
            'legend.edgecolor': '#3a3f45',
            'legend.fontsize': 10,
            'legend.labelcolor': 'white',
            'legend.framealpha': 0.9,
            'xtick.direction': 'out',
            'ytick.direction': 'out',
        })

    def _load_data(self):
        """Load weather and location data."""
        try:
            fetcher = data_fetcher.DataFetcher(self.id)
            self.meteo_data = fetcher.get_meteo_data()
            self.location = data_fetcher.get_current(self.id)

            if not self.meteo_data:
                print("No weather data available for display")
                return False

            self._extract_weather_data()
            self._load_sun_data(fetcher)
            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def _extract_weather_data(self):
        """Extract weather data from API response."""
        hourly = self.meteo_data.get("hourly", {})
        self.temps = hourly.get("temperature_2m", [])
        self.apparent_temps = hourly.get("apparent_temperature", [])
        self.times = [datetime.fromisoformat(t) for t in hourly.get("time", [])]
        self.shifted_times = [t - timedelta(minutes=30) for t in self.times]
        self.rain = hourly.get("rain", [])
        self.cloud_cover = hourly.get("cloud_cover", [])
        self.day = hourly.get("is_day", [])


        # Calculate time range
        self.now = datetime.now()
        self.end_time = self.now + timedelta(hours=self.CHART_HOURS)

        # Temperature range for plotting
        self.temp_min = min(min(self.temps), min(self.apparent_temps))
        self.temp_max = max(max(self.temps), max(self.apparent_temps))

    def _load_sun_data(self, fetcher):
        """Load sunrise and sunset data for all days in chart range."""
        self.sun_markers = []
        chart_dates = self._get_chart_dates()

        for date in chart_dates:
            date_str = date.strftime('%Y-%m-%d')
            try:
                sun_data = fetcher.get_sun_data(date_str)
                if sun_data and 'results' in sun_data:
                    self._parse_sun_times(sun_data['results'], date)
            except Exception as e:
                print(f"Error fetching sun data for {date}: {e}")

        print(f"Debug - Found {len(self.sun_markers)} sun markers")

    def _get_chart_dates(self):
        """Get list of dates covered by the chart."""
        dates = []
        current_date = self.now.date()
        end_date = self.end_time.date()

        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        return dates

    def _parse_sun_times(self, sun_data, date):
        """Parse sunrise and sunset times for a given date."""
        sunset = sun_data.get('sunset')
        sunrise = sun_data.get('sunrise')

        if sunset:
            try:
                sunset_time = datetime.strptime(sunset, '%I:%M:%S %p').time()
                sunset_dt = datetime.combine(date, sunset_time)
                if self.now <= sunset_dt <= self.end_time:
                    self.sun_markers.append(('sunset', sunset_dt))
            except ValueError:
                print(f"Could not parse sunset time: {sunset} for date {date}")

        if sunrise:
            try:
                sunrise_time = datetime.strptime(sunrise, '%I:%M:%S %p').time()
                sunrise_dt = datetime.combine(date, sunrise_time)
                if self.now <= sunrise_dt <= self.end_time:
                    self.sun_markers.append(('sunrise', sunrise_dt))
            except ValueError:
                print(f"Could not parse sunrise time: {sunrise} for date {date}")

    def _create_plot(self):
        """Create the main weather plot."""
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.figure.patch.set_alpha(0.0)
        self.ax.patch.set_alpha(0.5)

        # Create smooth interpolated data
        self._create_smooth_data()

        # Add plot elements
        self._add_day_night_background()
        self._add_cloud_coverage()
        self._add_temperature_lines()
        self._add_precipitation()
        self._add_sun_markers()
        self._configure_axes()
        self._add_temperature_labels()
        self._add_grid_and_legend()
        self._set_title_and_labels()
        self._adjust_layout()

    def _create_smooth_data(self):
        """Create smooth interpolated data for plotting."""
        time_nums = mdates.date2num(self.times)
        self.time_nums_smooth = np.linspace(time_nums[0], time_nums[-1], len(time_nums) * 6)
        self.times_smooth = mdates.num2date(self.time_nums_smooth)

        # Cubic spline interpolation for smooth curves
        f_temp = interp1d(time_nums, self.temps, kind='cubic', fill_value='extrapolate')
        self.temps_smooth = f_temp(self.time_nums_smooth)

        f_apparent = interp1d(time_nums, self.apparent_temps, kind='cubic', fill_value='extrapolate')
        self.apparent_temps_smooth = f_apparent(self.time_nums_smooth)

        f_clouds = interp1d(time_nums, self.cloud_cover, kind='cubic', fill_value='extrapolate')
        self.cloud_cover_smooth = f_clouds(self.time_nums_smooth)

    def _add_day_night_background(self):
        """Add day/night background based on sunrise/sunset times."""

        # Apply day/night background
        for i in range(len(self.times) - 1):
            start_time = self.times[i]
            end_time = self.times[i + 1]
            color = '#2a2e35' if self.day[i] else '#1a1c1e'
            alpha = 0.3 if self.day[i] else 0.5

            self.ax.axvspan(start_time, end_time, color=color, alpha=alpha, zorder=-1)

    def _add_cloud_coverage(self):
        """Add cloud coverage as secondary y-axis."""
        self.ax_clouds = self.ax.twinx()

        self.ax_clouds.plot(
            self.times_smooth,
            self.cloud_cover_smooth,
            color=self.CLOUD_COLOR,
            alpha=0.6,
            linewidth=1.5,
            linestyle='--',
            label="Cloud Cover [%]",
            zorder=3
        )

        # Configure cloud cover axis
        self.ax_clouds.set_ylim(0, 500)
        self.ax_clouds.set_ylabel('Cloud Cover [%]', color=self.CLOUD_COLOR, labelpad=15)
        self.ax_clouds.tick_params(axis='y', labelcolor=self.CLOUD_COLOR)
        self.ax_clouds.set_yticks([100])
        self.ax_clouds.set_yticklabels(['100'])
        self.ax_clouds.spines['right'].set_alpha(0.3)
        self.ax_clouds.spines['right'].set_color(self.CLOUD_COLOR)

        # Add subtle fill area
        self.ax_clouds.fill_between(
            self.times_smooth,
            0,
            self.cloud_cover_smooth,
            color=self.CLOUD_COLOR,
            alpha=0.08,
            zorder=1
        )

    def _add_temperature_lines(self):
        """Add temperature and apparent temperature lines with fill."""
        # Temperature lines
        self.ax.plot(
            self.times_smooth,
            self.temps_smooth,
            color=self.MAIN_COLOR,
            label='Temperature [°C]',
            zorder=4
        )

        self.ax.plot(
            self.times_smooth,
            self.apparent_temps_smooth,
            color=self.APPARENT_COLOR,
            linestyle=':',
            label='Feels Like [°C]',
            zorder=4
        )

        # Fill between lines
        self.ax.fill_between(
            self.times_smooth,
            self.temps_smooth,
            self.apparent_temps_smooth,
            where=np.array(self.temps_smooth) > np.array(self.apparent_temps_smooth),
            interpolate=True,
            color=self.MAIN_COLOR,
            alpha=0.15,
            zorder=3
        )

        self.ax.fill_between(
            self.times_smooth,
            self.temps_smooth,
            self.apparent_temps_smooth,
            where=np.array(self.temps_smooth) <= np.array(self.apparent_temps_smooth),
            interpolate=True,
            color=self.APPARENT_COLOR,
            alpha=0.15,
            zorder=3
        )

    def _add_precipitation(self):
        """Add precipitation bars if rain data exists."""
        self.ax_rain = None
        if any(self.rain):
            self.ax_rain = self.ax.twinx()

            max_rain_value = max(self.rain) if max(self.rain) > 0 else 1
            self.ax_rain.set_ylim(0, max_rain_value * 8)
            self.ax_rain.set_ylabel('Precipitation [mm]', color=self.RAIN_COLOR)
            self.ax_rain.tick_params(axis='y', labelcolor=self.RAIN_COLOR)

            # Rain bars
            self.ax_rain.bar(
                self.shifted_times,
                self.rain,
                width=0.03,
                color=self.RAIN_COLOR,
                alpha=0.6,
                label='Precipitation [mm]',
                zorder=4
            )

            # Rain value labels
            for x, r_val in zip(self.shifted_times, self.rain):
                if r_val > 0.0 and self.now < x < self.end_time:
                    self.ax_rain.text(
                        x,
                        r_val + max_rain_value * 0.02,
                        f"{r_val:.1f}",
                        ha='center',
                        va='bottom',
                        fontsize=7,
                        color=self.RAIN_COLOR,
                        zorder=5
                    )

    def _add_sun_markers(self):
        """Add sunrise and sunset markers at the top of chart."""
        y_top = self.temp_max + 2.5

        for marker_type, marker_dt in self.sun_markers:
            if marker_type == 'sunset':
                color = self.SUNSET_COLOR
            elif marker_type == 'sunrise':
                color = self.SUNRISE_COLOR
            else:
                continue

            # Vertical line
            self.ax.axvline(marker_dt, color=color, linestyle=':', alpha=0.7, linewidth=2, zorder=6)

            # Time annotation
            self.ax.annotate(
                f"{marker_dt.strftime('%H:%M')}",
                (marker_dt, y_top),
                xytext=(0, 15),
                textcoords='offset points',
                ha='center',
                va='bottom',
                fontsize=9,
                color=color,
                weight='bold',
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor=(26 / 255, 28 / 255, 30 / 255, 0.8),
                    edgecolor=color,
                    linewidth=1,
                    alpha=0.9
                ),
                zorder=7
            )

    def _configure_axes(self):
        """Configure x and y axes."""
        # X-axis configuration
        self.ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # Secondary x-axis for dates
        self.ax2 = self.ax.secondary_xaxis('bottom')
        self.ax2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 24]))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        self.ax2.tick_params(axis='x', which='major', pad=25, labelsize=8, colors='#b0b0b0')

        self.ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
        self.ax.set_xlim(left=self.now, right=self.end_time)

        # Y-axis configuration
        self.ax.set_ylim(self.temp_min - 2, self.temp_max + 3)
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(4))
        self.ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

    def _add_temperature_labels(self):
        """Add temperature value labels on the chart."""
        bbox_color = (26 / 255, 28 / 255, 30 / 255, 0.7)

        for x, y in zip(self.shifted_times, self.temps):
            if self.now <= x <= self.end_time and x.hour % 1 == 0:
                self.ax.annotate(
                    f"{y:.0f}°",
                    (x, y),
                    xytext=(0, 12),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    fontsize=8,
                    color=self.MAIN_COLOR,
                    weight='bold',
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor=bbox_color,
                        edgecolor='none',
                        alpha=0.7
                    ),
                    zorder=5
                )

    def _add_grid_and_legend(self):
        """Add grid lines and legend."""
        # Zero line and grid
        self.ax.axhline(0, color='#5a5f65', linestyle='-', alpha=0.3, zorder=2)
        self.ax.grid(which='major', alpha=0.7, zorder=2)
        self.ax.grid(which='minor', alpha=0.3, linestyle=':', zorder=2)

        # Legend
        lines, labels = self.ax.get_legend_handles_labels()
        lines_clouds, labels_clouds = self.ax_clouds.get_legend_handles_labels()

        if self.ax_rain is not None:
            lines_rain, labels_rain = self.ax_rain.get_legend_handles_labels()
            lines.extend(lines_clouds + lines_rain)
            labels.extend(labels_clouds + labels_rain)
        else:
            lines.extend(lines_clouds)
            labels.extend(labels_clouds)

        self.ax.legend(lines, labels, loc='upper right', frameon=True)

    def _set_title_and_labels(self):
        """Set chart title and axis labels."""
        self.ax.set_title(
            f"Temperature Forecast - {self.location['Name']}",
            fontsize=12,
            pad=35,
            color='#f0f0f0',
            fontweight='bold'
        )

        self.ax.set_xlabel("Time [Hours]", labelpad=10)
        self.ax.set_ylabel("Temperature [°C]", labelpad=10)

    def _adjust_layout(self):
        """Adjust plot layout and margins."""
        self.figure.subplots_adjust(
            left=0.08,
            right=0.92,
            top=0.82,
            bottom=0.20
        )

class HydroPlot(FigureCanvas):

    def __init__(self, id, parent=None):
        super().__init__(parent)

        self.MAIN_COLOR = '#ff4f64'
        self.APPARENT_COLOR = '#5bc0ff'
        self.RAIN_COLOR = '#4da6ff'
        self.CLOUD_COLOR = '#888888'
        self.SUNSET_COLOR = '#ff6b35'
        self.SUNRISE_COLOR = '#ffb347'

        self.id = id
        self._setup_matplotlib_style()
        if self._load_data():
            self._create_plot()
