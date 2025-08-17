import math as m


def calc_distance(lat_a, lon_a, lat_b, lon_b):
    lat_a, lon_a, lat_b, lon_b = map(m.radians, [lat_a, lon_a, lat_b, lon_b])

    dlat = lat_b - lat_a
    dlon = lon_b - lon_a

    a = m.sin(dlat / 2) ** 2 + m.cos(lat_a) * m.cos(lat_b) * m.sin(dlon / 2) ** 2
    c = 2 * m.atan2(m.sqrt(a), m.sqrt(1 - a))
    return 6371 * c


def find_closest(lat, lon, dict_of_loc):
    return min(
        dict_of_loc,
        key=lambda city: calc_distance(
            lat, lon,
            city["Latitude"],
            city["Longitude"]
        ) if city["Type"] == "city" else float("inf")
    )
