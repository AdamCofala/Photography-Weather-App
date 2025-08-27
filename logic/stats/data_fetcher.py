import requests
import logic.utils.location_base as loc
import logic.utils.haversine as hv


def get_current(id):
    locations = loc.get_locations("assets/config.json")
    return locations[id]


def get_hydro_list():
    try:
        url = f"https://raw.githubusercontent.com/AdamCofala/polish-hydro-data/refs/heads/master/stations_list.json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


class DataFetcher:
    def __init__(self, id):
        self.meteo_data = {}
        self.sun_data = {}
        self.hydro_data = {}
        self.location = get_current(id)

    def get_meteo_data(self):
        self.request_meteo_data()
        return self.meteo_data

    def get_sun_data(self, date):
        self.request_sun_data(date)
        return self.sun_data

    def get_hydro_data(self):
        self.request_hydro_data(self.find_closest_station_id())
        return self.hydro_data

    def request_meteo_data(self):
        try:
            url = f'https://api.open-meteo.com/v1/forecast?latitude={self.location["Lat"]}&longitude={self.location["Lon"]}&hourly=temperature_2m,rain,weather_code,cloud_cover,apparent_temperature,is_day&models=ecmwf_ifs025&past_days=0&forecast_days=3'
            response = requests.get(url)
            response.raise_for_status()
            self.meteo_data = response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def request_sun_data(self, date):
        try:
            url = f'https://api.sunrisesunset.io/json?lat={self.location["Lat"]}&lng={self.location["Lon"]}&date={date}'
            response = requests.get(url)
            response.raise_for_status()
            self.sun_data = response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def request_hydro_data(self, station_id):
        try:
            url = f"https://raw.githubusercontent.com/AdamCofala/polish-hydro-data/refs/heads/master/data/{station_id}.json"
            response = requests.get(url)
            response.raise_for_status()
            self.hydro_data = response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

    def find_closest_station_id(self):
        stations_list = get_hydro_list()
        return hv.find_closest_hydrostation(self.location["Lat"],self.location["Lon"], stations_list)['id']


