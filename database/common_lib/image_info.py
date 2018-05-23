from datetime import datetime

from PIL.ExifTags import TAGS, GPSTAGS

from database.common_lib import city_location


class ImageInfo:
    def __init__(self):
        """ Initial """
        self._city = city_location.CityLocation()

    def get_exif_data(self, image):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        exif_data = {}
        try:
            info = image._getexif()
        except Exception:
            info = None
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value

        return exif_data

    def _get_if_exist(self, data, key):
        if key in data:
            return data[key]

        return None

    def _convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lon(self, exif_data):
        """Returns the latitude and longitude, if available, from the provided exif_data
        (obtained through get_exif_data above)"""
        lat = None
        lon = None

        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]

            gps_latitude = self._get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = self._get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = self._get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = self._get_if_exist(gps_info, 'GPSLongitudeRef')

            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self._convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat

                lon = self._convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon

        return lat, lon

    def get_date_taken(self, image):
        """ Return taken time with millisecond """
        try:
            info = image._getexif()
        except Exception:
            info = None

        if info:
            taken_time = self._get_minimum_creation_time(image._getexif())
            d = datetime.strptime(taken_time, "%Y:%m:%d %H:%M:%S").strftime('%s.%f')
            return d
        else:
            return None

    def _get_minimum_creation_time(self,exif_data):
        mtime = "?"
        if 306 in exif_data and exif_data[306] < mtime:  # 306 = DateTime
            mtime = exif_data[306]
        if 36867 in exif_data and exif_data[36867] < mtime:  # 36867 = DateTimeOriginal
            mtime = exif_data[36867]
        if 36868 in exif_data and exif_data[36868] < mtime:  # 36868 = DateTimeDigitized
            mtime = exif_data[36868]
        return mtime

    def get_city_location(self,lat,lon):
        """ Return lat,long nearest city """
        if lat is None and lon is None:
            return None
        city = self._city.nearest_city(lat,lon)
        return city.city_name

################
# Example ######
################
# import googlemapsget_exif_data
# if __name__ == "__main__":
#
#     imageinfo = ImageInfo()
#
#     image = Image.open("/Users/Terry/Desktop/MySQLFIles/ncs.jpg")  # load an image through PIL's Image object
#     exif_data = imageinfo.get_exif_data(image)
#
#     lat,lon = imageinfo.get_lat_lon(exif_data)
#
#     print(lat,lon)


# ## google api
# gmaps = googlemaps.Client(key='AIzaSyBNzdF5V16GPGlUdWr6nGbWgJwxUC5UxDg')
#
# reverse_geocode_result = gmaps.reverse_geocode((lat,lon))
# jj = json.dumps(reverse_geocode_result)
# data2 = json.loads(jj)
# print(data2[4]['formatted_address'])
