import json
import os

def get_locations(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as config:
                return json.load(config)
        except (json.JSONDecodeError, TypeError):
            return []

def remove_loc(path, id):
    locations = get_locations(path)

    new_loc = []
    deleted = False

    for loc in locations:
        if loc["ID"] == id:
            deleted = True
            continue
        if deleted:
            loc["ID"] -= 1
        new_loc.append(loc)

    with open(path, "w") as config:
        json.dump(new_loc, config, indent=4)

class Location:

    _next_id = None

    @classmethod
    def _init_id(cls, path):
        exist = get_locations(path)
        if len(exist) > 0:
            max_id =max(loc.get("ID", 0) for loc in exist)
            cls._next_id = max_id + 1
        else:
            cls._next_id = 0

    def __init__(self, name, lat, lon, time, path):
        Location._init_id(path)

        self.path = path
        self.Name = name
        self.Lat = lat
        self.Lon = lon
        self.Time = time
        self.id = Location._next_id
        Location._next_id += 1

    def to_dict(self):
        return {"ID": self.id, "Name": self.Name, "Lat": self.Lat, "Lon": self.Lon, "Time": self.Time}

    def to_json(self):
        locations = get_locations(self.path)
        locations.append(self.to_dict())

        with open(self.path, "w") as config:
            json.dump(locations, config, indent=4)




if __name__ == '__main__':
    # loc = Location("Skibidi", 32.221, 323.23, "dada")
    # loc1 = Location("sigma boy", 32.221, 323.23, "dada")
    # loc2 = Location("adadjs", 32.221, 323.23, "dada")
    # loc3 = Location("dadadad", 32.221, 323.23, "dada")
    # loc.to_json("config.json")
    # loc1.to_json("config.json")
    # loc2.to_json("config.json")
    # loc3.to_json("config.json")
    remove_loc("config.json", 2)






