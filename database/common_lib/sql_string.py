import math
import os

from PIL import Image

from database.common_lib import dictionary, image_info
import ffprobe3
from tinytag import TinyTag


class SqlString:
    def __init__(self, home_path):
        """ Initial """

        self._dict = dictionary.Dictionary()
        self._image_info = image_info.ImageInfo()
        self._home_path = home_path

    def _convert_size(self, size_bytes):
        """ Convert Size to Bytes """

        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def get_create_summary_table_str(self):
        """ Return create summary table SQL command """

        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,user VARCHAR(40) NOT NULL," \
                  "type VARCHAR(20) NOT NULL,source_name VARCHAR(100) NOT NULL,nickname VARCHAR(100) NOT NULL," \
                  "source_path VARCHAR(200) NOT NULL,nas_path VARCHAR(200) NOT NULL,c_time INT NOT NULL," \
                  "m_time INT NOT NULL,a_time INT NOT NULL,size VARCHAR(20) NOT NULL,device_id VARCHAR(40) NOT NULL," \
                  "upload_mode VARCHAR(20) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def get_create_type_table_str(self, user_name, file_type):
        """ Return create type table SQL command """

        sql_str = "CREATE TABLE "
        sql_str += user_name
        sql_str += "_"
        sql_str += file_type
        sql_str += self._dict.type_create_struct(file_type)
        return sql_str

    def get_insert_tables_str(self, file_name, user_name, device_id, source_path, upload_mode, source_name=None):
        """ Return Instert tables SQL command """

        filename, file_extension = os.path.splitext(file_name)

        file_extension = file_extension.strip('.')

        nas_user_path = self._home_path + "/"
        nas_user_path += str(user_name)

        c_time = os.stat(nas_user_path + "/" + file_name).st_ctime
        m_time = os.stat(nas_user_path + "/" + file_name).st_mtime
        a_time = os.stat(nas_user_path + "/" + file_name).st_atime

        summary_sql = "INSERT INTO summary(user,type,nickname,source_path,nas_path,c_time,m_time,a_time,size," \
                      "device_id,upload_mode,source_name) VALUES(\""

        # to lower case, cause some file_extension save as upper case
        file_type = self._dict.get_file_type(str.lower(file_extension))

        summary_sql += user_name
        summary_sql += "\",\""
        summary_sql += file_type
        summary_sql += "\",\""
        summary_sql += file_name
        summary_sql += "\",\""
        summary_sql += source_path
        summary_sql += "\",\""
        summary_sql += nas_user_path
        summary_sql += "\","
        summary_sql += str(c_time)
        summary_sql += ","
        summary_sql += str(m_time)
        summary_sql += ","
        summary_sql += str(a_time)
        summary_sql += ",\""
        summary_sql += self._convert_size(os.stat(nas_user_path + "/" + file_name).st_size)
        summary_sql += "\",\""
        summary_sql += device_id
        summary_sql += "\",\""
        summary_sql += upload_mode
        summary_sql += "\",\""
        if source_name is None:
            summary_sql += file_name
        else:
            summary_sql += source_name
        summary_sql += "\") "

        # Find by name & path double check
        user_type_table = user_name + "_"
        user_type_table += file_type

        type_sql = "INSERT INTO "
        type_sql += user_type_table
        type_sql += self._dict.type_insert_struct(file_type)
        type_sql += " SELECT id "

        if file_type == 'image':
            # Set set thumbnail

            image = Image.open(nas_user_path + "/" + file_name)  # load an image through PIL's Image object
            exif_data = self._image_info.get_exif_data(image)
            lat, lon = self._image_info.get_lat_lon(exif_data)
            time = self._image_info.get_date_taken(image)
            city = self._image_info.get_city_location(lat, lon)

            if time is None:
                time = 'NULL'
            if lat is None:
                lat = 'NULL'
            if lon is None:
                lon = 'NULL'
            if city is None:
                city = 'NULL'
            type_sql += ","
            type_sql += str(lat)
            type_sql += ","
            type_sql += str(lon)
            type_sql += ",\'"
            type_sql += str(city)
            type_sql += "\',"
            type_sql += str(time)

        if file_type == 'video':
            duration = 'NULL'
            try:
                metadata = ffprobe3.FFProbe(nas_user_path + "/" + file_name)
                for stream in metadata.streams:
                    if stream.is_video():
                        duration = str(stream.duration_seconds())
            except:
                pass
            type_sql += ','
            type_sql += duration

        if file_type == 'music':
            title = 'NULL'
            album = 'NULL'
            artist = 'NULL'
            duration = 'NULL'
            samplerate = 'NULL'
            try:
                tag = TinyTag.get(nas_user_path + "/" + file_name)
                if tag.title:
                    title = tag.title
                if tag.album:
                    album = tag.album
                if tag.artist:
                    artist = tag.artist
                if tag.duration:
                    duration = tag.duration
                if tag.samplerate:
                    samplerate = tag.samplerate
            except:
                pass
            type_sql += ",\""
            type_sql += title
            type_sql += "\",\""
            type_sql += album
            type_sql += "\",\""
            type_sql += artist
            type_sql += "\","
            type_sql += str(duration)
            type_sql += ","
            type_sql += str(samplerate)

        type_sql += " From summary where summary.nickname=\""
        type_sql += file_name
        type_sql += "\";"
        return summary_sql, type_sql

    def get_insert_folder_str(self, path, folder_name, user_name):
        """ Return Instert tables SQL command
            folder need special treatment
            * Now Size is NULL
            TODO : maybe can sum files under the folder to be this folder's size
        """

        c_time = os.stat(path + "/" + folder_name).st_ctime
        m_time = os.stat(path + "/" + folder_name).st_mtime
        a_time = os.stat(path + "/" + folder_name).st_atime

        folder_sql = "INSERT INTO summary(user,type,name,path,c_time,m_time,a_time,size) VALUES(\""
        folder_sql += user_name
        folder_sql += "\",\"folder\",\""
        folder_sql += folder_name
        folder_sql += "\", \""
        folder_sql += path
        folder_sql += "\","
        folder_sql += str(c_time)
        folder_sql += ","
        folder_sql += str(m_time)
        folder_sql += ","
        folder_sql += str(a_time)
        folder_sql += ",\""
        folder_sql += self._convert_size(os.stat(path + "/" + folder_name).st_size)
        folder_sql += "\") "

        type_sql = "INSERT INTO "
        type_sql += user_name
        type_sql += "_"
        type_sql += "folder"
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += folder_name
        type_sql += "\" AND path=\""
        type_sql += path
        type_sql += "\";"

        return folder_sql, type_sql

    def get_user_file_type_str(self, user_name, file_type):
        """ Return user_type table's name,path,m_time SQL command """
        table_str = user_name + "_"
        table_str += file_type

        sql = "SELECT summary.id,type,nickname,nas_path,m_time,size,device_id,upload_mode"
        if file_type == 'image':
            sql += ","
            sql += table_str
            sql += ".latitude"
            sql += ","
            sql += table_str
            sql += ".longitude"
            sql += ","
            sql += table_str
            sql += ".city"
            sql += ","
            sql += table_str
            sql += ".taken_time"
            sql += ","
            sql += table_str
            sql += ".face_id"
        elif file_type == 'video':
            sql += ","
            sql += table_str
            sql += ".duration"
        elif file_type == 'music':
            sql += ","
            sql += table_str
            sql += ".title"
            sql += ","
            sql += table_str
            sql += ".album"
            sql += ","
            sql += table_str
            sql += ".artist"
            sql += ","
            sql += table_str
            sql += ".duration"
            sql += ","
            sql += table_str
            sql += ".samplerate"

        sql += " FROM summary INNER JOIN "
        sql += table_str
        sql += " ON summary.id = "
        sql += user_name
        sql += "_"
        sql += file_type
        sql += ".summary_id;"
        return sql

    def get_files_under_folder_str(self, folder_path):
        """ Return files id under folder SQL command """
        sql = "SELECT id,type,nickname,nas_path,m_time,size,device_id,upload_mode FROM summary " \
              "WHERE nas_path=\"" + folder_path
        sql += "\";"
        return sql

    def get_create_user_table_str(self):
        """ Return create user table SQL command """
        sql_str = "CREATE TABLE users(id INT NOT NULL AUTO_INCREMENT,name VARCHAR(40) NOT NULL,PRIMARY KEY (id))"
        return sql_str

    def get_insert_user_table_str(self, user_name):
        """ Return insert user table SQL command """
        sql_str = "INSERT INTO users(name) VALUES(\""
        sql_str += user_name
        sql_str += "\");"
        return sql_str

    def get_select_user_table_str(self):
        """ Return select user table SQL command """
        sql_str = "SELECT * FROM users;"
        return sql_str

    def get_file_path_with_id_str(self, summary_id):
        """ Return file's path with id """
        sql_str = "SELECT nas_path,nickname FROM summary WHERE id="
        sql_str += str(summary_id)
        return sql_str

    # def get_check_file_already_exist_str(self, path, file_name, user_name):
    #     """ Return fetch from summary  """
    #     sql_str = 'SELECT id FROM summary WHERE nickname=\''
    #     sql_str += file_name
    #     sql_str += '\' AND path=\''
    #     sql_str += path
    #     sql_str += '\' AND user=\''
    #     sql_str += user_name
    #     sql_str += '\';'
    #     return sql_str

    def get_update_file_table_str(self, file_name, user_name, summary_id):
        """ Return update summary & type talbe str """

        filename, file_extension = os.path.splitext(file_name)

        file_extension = file_extension.strip('.')

        nas_user_path = self._home_path + "/"
        nas_user_path += str(user_name)

        c_time = os.stat(nas_user_path + "/" + file_name).st_ctime
        m_time = os.stat(nas_user_path + "/" + file_name).st_mtime
        a_time = os.stat(nas_user_path + "/" + file_name).st_atime

        summary_sql = "UPDATE summary SET type=\""

        # to lower case, cause some file_extension save as upper case
        file_type = self._dict.get_file_type(str.lower(file_extension))

        summary_sql += file_type
        summary_sql += "\",c_time="
        summary_sql += str(c_time)
        summary_sql += ",m_time="
        summary_sql += str(m_time)
        summary_sql += ",a_time="
        summary_sql += str(a_time)
        summary_sql += ",size=\""
        summary_sql += self._convert_size(os.stat(nas_user_path + "/" + file_name).st_size)
        summary_sql += "\",nickname=\""
        summary_sql += file_name
        summary_sql += "\" WHERE id="
        summary_sql += str(summary_id)
        summary_sql += ";"

        type_sql = ""
        if file_type == 'image':
            # Set set thumbnail

            image = Image.open(nas_user_path + "/" + file_name)  # load an image through PIL's Image object
            exif_data = self._image_info.get_exif_data(image)
            lat, lon = self._image_info.get_lat_lon(exif_data)
            time = self._image_info.get_date_taken(image)
            city = self._image_info.get_city_location(lat, lon)

            if time is None:
                time = 'NULL'
            if lat is None:
                lat = 'NULL'
            if lon is None:
                lon = 'NULL'
            if city is None:
                city = 'NULL'

            type_sql += "UPDATE "
            type_sql += user_name
            type_sql += "_"
            type_sql += file_type
            type_sql += " SET latitude="
            type_sql += str(lat)
            type_sql += ",longitude="
            type_sql += str(lon)
            type_sql += ",city=\'"
            type_sql += str(city)
            type_sql += "\',taken_time="
            type_sql += str(time)
            type_sql += " WHERE summary_id="
            type_sql += str(summary_id)
            type_sql += ";"

        if file_type == 'video':
            duration = 'NULL'
            try:
                metadata = ffprobe3.FFProbe(nas_user_path + "/" + file_name)
                for stream in metadata.streams:
                    if stream.is_video():
                        duration = str(stream.duration_seconds())
            except:
                pass
            type_sql += "UPDATE "
            type_sql += user_name
            type_sql += "_"
            type_sql += file_type
            type_sql += " SET duration="
            type_sql += duration
            type_sql += " WHERE summary_id="
            type_sql += str(summary_id)
            type_sql += ";"

        if file_type == 'music':

            title = 'NULL'
            album = 'NULL'
            artist = 'NULL'
            duration = 'NULL'
            samplerate = 'NULL'
            try:
                tag = TinyTag.get(nas_user_path + "/" + file_name)
                if tag.title:
                    title = tag.title
                if tag.album:
                    album = tag.album
                if tag.artist:
                    artist = tag.artist
                if tag.duration:
                    duration = tag.duration
                if tag.samplerate:
                    samplerate = tag.samplerate
            except:
                pass

            type_sql += "UPDATE "
            type_sql += user_name
            type_sql += "_"
            type_sql += file_type
            type_sql += " SET title=\""
            type_sql += title
            type_sql += "\",album=\""
            type_sql += album
            type_sql += "\",artist=\""
            type_sql += artist
            type_sql += "\",duration="
            type_sql += duration
            type_sql += ",samplerate="
            type_sql += samplerate
            type_sql += " WHERE summary_id="
            type_sql += str(summary_id)
            type_sql += ";"

        return summary_sql, type_sql

    def get_info_by_summaryid_str(self, summary_id):
        """ Return file's user,type with id """
        sql_str = "SELECT user,type FROM summary WHERE id="
        sql_str += str(summary_id)
        sql_str += ";"
        return sql_str

    def get_initial_str(self):
        drop_sql_str = "DROP DATABASE IF EXISTS mydatabase;"
        create_sql_str = "CREATE DATABASE mydatabase CHARACTER SET utf8;"
        return drop_sql_str, create_sql_str

    def get_delete_summary_type_with_id_str(self, user_table, summary_id):
        """ Return delete 2 table sql cmd """
        sql_str = 'DELETE summary,'
        sql_str += user_table
        sql_str += ' FROM summary INNER JOIN '
        sql_str += user_table
        sql_str += ' WHERE summary.id='
        sql_str += user_table
        sql_str += '.summary_id AND summary.id='
        sql_str += str(summary_id)
        sql_str += ';'
        return sql_str

    def get_face_id_update_str(self, file_path, user_name, face_id):
        """ Return update image's face sql cmd """
        path, file = os.path.split(file_path)

        sql_str = "UPDATE "
        sql_str += user_name
        sql_str += "_image"
        sql_str += " AS t INNER JOIN summary AS s ON t.summary_id=s.id SET face_id="
        sql_str += str(face_id)
        sql_str += " WHERE s.nickname=\""
        sql_str += file
        sql_str += "\" AND s.nas_path=\""
        sql_str += path
        sql_str += "\";"
        return sql_str

    def get_update_file_with_id_str(self, file_path, summary_id, user_table):
        """ Return update summary & type table sql cmd """
