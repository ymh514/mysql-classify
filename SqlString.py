import time
import Dictionary
import math
import os

class TypeStruct:
    def typeCreateStruct(self,type):
        return {
            'Picture': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,latitude FLOAT(6) DEFAULT NULL,longitude FLOAT(6) DEFAULT NULL,PRIMARY KEY (id));',
            'Video': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'Music': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'Document': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'Other': '(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));',
            'Folder':'(id INT NOT NULL AUTO_INCREMENT,summary_id INT NOT NULL,PRIMARY KEY (id));'
        }.get(type)
    def typeInsertStruct(self,type):
        return {
            'Picture': 'picture',
            'Video': 'video',
            'Music': 'music',
            'Document': 'document',
            'Other': 'other',
            'Folder':'folder'
        }.get(type)

class SqlString:

    def __init__(self):
        """ Initial """

        self._dict= Dictionary.Dictionary()
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

        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,type VARCHAR(20) NOT NULL,name VARCHAR(100) NOT NULL,path VARCHAR(80) NOT NULL,mtime DATETIME NOT NULL,size VARCHAR(20) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def getCreateTypeTableStr(self, type_name):
        """ Return create type table SQL command """

        sql_str = "CREATE TABLE "
        sql_str += self._dict.getTableName(type_name)
        # sql_str += "(id INT NOT NULL AUTO_INCREMENT,summary_id INT UNSIGNED NOT NULL,PRIMARY KEY (id));"
        sql_str += self._typeStruct.typeCreateStruct(type_name)
        return sql_str

    def getInsertTablesStr(self, path, file):
        """ Return Instert tables SQL command """

        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        mtime = os.stat(path + "/" + file).st_mtime
        mtime2 = time.localtime(mtime)
        mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

        ## 5. type 1. name 2. mtime 3. size 4. path
        summary_sql = "INSERT INTO summary(type,name,path,mtime,size) VALUES(\""

        file_type = self._dict.getFileType(file_extension)

        summary_sql += file_type
        summary_sql += "\",\""
        summary_sql += file
        summary_sql += "\",\""
        summary_sql += path
        summary_sql += "\",STR_TO_DATE(\""
        summary_sql += mtime2_hr
        summary_sql += "\",\"%m/%d/%Y %T\"),\""
        summary_sql += self._convert_size(os.stat(path + "/" + file).st_size)
        summary_sql += "\") "

        # Find by name & path double check
        type_sql = "INSERT INTO "
        type_sql += self._dict.getTableName(file_type)
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += file
        type_sql += "\" AND path=\""
        type_sql += path
        type_sql += "\";"

        return summary_sql,type_sql

    def getInsertFolderStr(self,path,folder):
        """ Return Instert tables SQL command
            folder need special treatment
            * Now Size is NULL
            TODO : maybe can sum files under the folder to be this folder's size
        """

        mtime = os.stat(path + "/" + folder).st_mtime
        mtime2 = time.localtime(mtime)
        mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

        summary_sql = "INSERT INTO summary(type,name,path,mtime,size) VALUES(\"Folder\",\""
        summary_sql += folder
        summary_sql += "\", \""
        summary_sql += path
        summary_sql += "\",STR_TO_DATE(\""
        summary_sql += mtime2_hr
        summary_sql += "\",\"%m/%d/%Y %T\"),\""
        summary_sql += self._convert_size(os.stat(path + "/" + folder).st_size)
        summary_sql += "\") "

        type_sql = "INSERT INTO folder"
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += folder
        type_sql += "\" AND path=\""
        type_sql += path
        type_sql += "\";"

        return summary_sql,type_sql

    def getSummaryTableStr(self):
        return "SELECT * FROM summary"

    def getTypeTableStr(self,type):
        return ""