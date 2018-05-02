import time
import Dictionary
import math
import os
import ImageInfo
from PIL import Image


class TypeStruct:
    def typeCreateStruct(self, type):
        return {
            'image': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,latitude FLOAT(6) DEFAULT NULL,longitude FLOAT(6) DEFAULT NULL,taken_time INT DEFAULT NULL,PRIMARY KEY (id));',
            'video': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'music': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'file': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'folder': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));'
        }.get(type)

    def typeInsertStruct(self, type):
        return {
            'image': '(summary_id,latitude,longitude,taken_time)',
            'video': '(summary_id)',
            'music': '(summary_id)',
            'file': '(summary_id)',
            'folder': '(summary_id)'
        }.get(type)
        # UPDATE image JOIN summary  ON (summary.id=image.summary_id) SET image.latitude = 213.123123 , image.longitude=555.1 WHERE summary.name="tmp.py"
        # insert into image (summary_id,latitude,longitude) select id,20.11,555 From summary where summary.name="tmp.py"
class SqlString:

    def __init__(self):
        """ Initial """

        self._dict = Dictionary.Dictionary()
        self._imageInfo = ImageInfo.ImageInfo()
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

    def getCreateSummaryTableStr(self):
        """ Return create summary table SQL command """

        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,type VARCHAR(20) NOT NULL,name VARCHAR(100) NOT NULL,path VARCHAR(200) NOT NULL,c_time INT NOT NULL,m_time INT NOT NULL,a_time INT NOT NULL,size VARCHAR(20) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def getCreateTypeTableStr(self, type_name):
        """ Return create type table SQL command """

        sql_str = "CREATE TABLE "
        sql_str += type_name
        sql_str += self._typeStruct.typeCreateStruct(type_name)
        return sql_str

    def getInsertTablesStr(self, path, file):
        """ Return Instert tables SQL command """

        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        c_time = os.stat(path + "/" + file).st_ctime
        m_time = os.stat(path + "/" + file).st_mtime
        a_time = os.stat(path + "/" + file).st_atime

        ## 5. type 1. name 2. mtime 3. size 4. path
        summary_sql = "INSERT INTO summary(type,name,path,c_time,m_time,a_time,size) VALUES(\""

        file_type = self._dict.getFileType(file_extension)

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
        type_sql += file_type
        type_sql += self._typeStruct.typeInsertStruct(file_type)
        type_sql += " SELECT id "

        if(file_type=='image'):
            image = Image.open(path +"/"+file)  # load an image through PIL's Image object
            exif_data = self._imageInfo.get_exif_data(image)

            lat, lon = self._imageInfo.get_lat_lon(exif_data)
            time = self._imageInfo.get_date_taken(image)

            if(time == None):
                time = 'NULL'
            if(lat == None):
                lat = 'NULL'
            if(lon == None):
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

    def getInsertFolderStr(self, path, folder):
        """ Return Instert tables SQL command
            folder need special treatment
            * Now Size is NULL
            TODO : maybe can sum files under the folder to be this folder's size
        """

        c_time = os.stat(path + "/" + folder).st_ctime
        m_time = os.stat(path + "/" + folder).st_mtime
        a_time = os.stat(path + "/" + folder).st_atime

        folder_sql = "INSERT INTO summary(type,name,path,c_time,m_time,a_time,size) VALUES(\"folder\",\""
        folder_sql += folder
        folder_sql += "\", \""
        folder_sql += path
        folder_sql += "\","
        folder_sql += str(c_time)
        folder_sql += ","
        folder_sql += str(m_time)
        folder_sql += ","
        folder_sql += str(a_time)
        folder_sql += ",\""
        folder_sql += self._convert_size(os.stat(path + "/" + folder).st_size)
        folder_sql += "\") "

        type_sql = "INSERT INTO folder"
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += folder
        type_sql += "\" AND path=\""
        type_sql += path
        type_sql += "\";"

        return folder_sql, type_sql


    def getDeleteTablesStr(self, path, file):
        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        file_type = self._dict.getFileType(file_extension)

        if file_extension=="":
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

    def getSummaryTableStr(self):
        return "SELECT * FROM summary"

    def getTypeTableStr(self, type):
        sql = "SELECT * FROM summary INNER JOIN "+type
        sql += " ON summary.id="
        sql += type
        sql += ".summary_id;"
        return sql
    def getPathFilesStr(self,path):
        sql = "SELECT * FROM summary WHERE path=\""+path
        sql += "\""
        return sql