import math
import os
from PIL import Image

import image_info
import dictionary


class TypeStruct:
    def type_create_struct(self, file_type):
        return {
            'image': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,latitude FLOAT(6) DEFAULT NULL,'
                     'longitude FLOAT(6) DEFAULT NULL,taken_time INT DEFAULT NULL,PRIMARY KEY (id));',
            'video': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'music': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'file': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'folder': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));'
        }.get(file_type)

    def type_insert_struct(self, file_type):
        return {
            'image': '(summary_id,latitude,longitude,taken_time)',
            'video': '(summary_id)',
            'music': '(summary_id)',
            'file': '(summary_id)',
            'folder': '(summary_id)'
        }.get(file_type)


class SqlString:
    def __init__(self):
        """ Initial """

        self._dict = dictionary.Dictionary()
        self._imageInfo = image_info.ImageInfo()
        self._typeStruct = TypeStruct()

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

        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,user VARCHAR(40) NOT NULL,type VARCHAR(20) NOT NULL,name VARCHAR(100) NOT NULL,path VARCHAR(200) NOT NULL,c_time INT NOT NULL,m_time INT NOT NULL,a_time INT NOT NULL,size VARCHAR(20) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def get_create_type_table_str(self, user_name, file_type):
        """ Return create type table SQL command """

        sql_str = "CREATE TABLE "
        sql_str += user_name
        sql_str += "_"
        sql_str += file_type
        sql_str += self._typeStruct.type_create_struct(file_type)
        return sql_str

    def get_insert_tables_str(self, path, file, user_name):
        """ Return Instert tables SQL command """

        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        c_time = os.stat(path + "/" + file).st_ctime
        m_time = os.stat(path + "/" + file).st_mtime
        a_time = os.stat(path + "/" + file).st_atime

        summary_sql = "INSERT INTO summary(user,type,name,path,c_time,m_time,a_time,size) VALUES(\""

        file_type = self._dict.get_file_type(file_extension)

        summary_sql += user_name
        summary_sql += "\",\""
        summary_sql += file_type
        summary_sql += "\",\""
        summary_sql += file
        summary_sql += "\",\""
        summary_sql += path
        summary_sql += "\","
        summary_sql += str(c_time)
        summary_sql += ","
        summary_sql += str(m_time)
        summary_sql += ","
        summary_sql += str(a_time)
        summary_sql += ",\""
        summary_sql += self._convert_size(os.stat(path + "/" + file).st_size)
        summary_sql += "\") "

        # Find by name & path double check
        type_sql = "INSERT INTO "
        type_sql += user_name
        type_sql += "_"
        type_sql += file_type
        type_sql += self._typeStruct.type_insert_struct(file_type)
        type_sql += " SELECT id "

        if file_type == 'image':
            image = Image.open(path + "/" + file)  # load an image through PIL's Image object
            exif_data = self._imageInfo.get_exif_data(image)

            lat, lon = self._imageInfo.get_lat_lon(exif_data)
            time = self._imageInfo.get_date_taken(image)

            if time is None:
                time = 'NULL'
            if lat is None:
                lat = 'NULL'
            if lon is None:
                lon = 'NULL'

            type_sql += ","
            type_sql += str(lat)
            type_sql += ","
            type_sql += str(lon)
            type_sql += ","
            type_sql += str(time)

        type_sql += " From summary where summary.name=\""
        type_sql += file
        type_sql += "\" AND path=\""
        type_sql += path
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

    def get_delete_tables_str(self, path, file):
        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        file_type = self._dict.get_file_type(file_extension)

        if file_extension == "":
            type_table = "folder"
        else:
            type_table = file_type

        sql = "DELETE summary,"
        sql += type_table
        sql += " FROM summary INNER JOIN "
        sql += type_table
        sql += " ON "
        sql += type_table
        sql += ".summary_id = summary.id WHERE summary.name=\""
        sql += file
        sql += "\" AND summary.path=\""
        sql += path
        sql += "\";"
        return sql

    def get_summary_table_str(self):
        return "SELECT * FROM summary"

    def get_summary_table_by_file_type_str(self, file_type):
        # TODO : rename
        sql = "SELECT * FROM summary INNER JOIN " + file_type
        sql += " ON summary.id="
        sql += file_type
        sql += ".summary_id;"
        return sql

    def get_path_files_str(self, path):
        sql = "SELECT * FROM summary WHERE path=\"" + path
        sql += "\""
        return sql

    def get_user_file_type_str(self, user_name, file_type):
        """ Return user_type table's name,path,m_time SQL command """
        sql = "SELECT summary.id,name,m_time FROM summary INNER JOIN " + user_name
        sql += "_"
        sql += file_type
        sql += " ON summary.id = "
        sql += user_name
        sql += "_"
        sql += file_type
        sql += ".summary_id;"
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

    def get_file_path_with_id_str(self, id):
        """ Return file's path with id """
        sql_str = "SELECT path,name FROM summary WHERE id="
        sql_str += str(id)
        return sql_str
