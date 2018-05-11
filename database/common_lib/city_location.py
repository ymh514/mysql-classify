import csv
import kdtree
import os


class City:
    '''
    City wraps up the info about a city, including its name, coordinates,
    and belonging country.
    '''

    def __init__(self, city_name, country_code):
        self.city_name = city_name
        self.country_code = country_code

class CityLocation:
    """ Get city location """

    def __init__(self):
        """ initial """
        # load the city data up
        _current_dir, _current_filename = os.path.split(__file__)
        _world_cities_csv_path = os.path.join(_current_dir,
                                              'simplemaps-worldcities-basic.csv')
        self._world_cities_kdtree = kdtree.create(dimensions=2)
        self.WORLD_CITIES_DICT = {}

        with open(_world_cities_csv_path, 'r') as csv_file:
            cities = csv.reader(csv_file)

            # discard the headers
            cities.__next__()

            # populate geo points into kdtree
            for city in cities:
                city_coordinate_key = (float(city[2]), float(city[3]))
                self._world_cities_kdtree.add(city_coordinate_key)
                c = City(city[0], city[5])
                self.WORLD_CITIES_DICT[city_coordinate_key] = c

    def nearest_city(self, latitude, longitude):
        """ Return city information """
        nearest_city_coordinate = self._world_cities_kdtree.search_nn((latitude, longitude,))
        return self.WORLD_CITIES_DICT[nearest_city_coordinate[0].data]
