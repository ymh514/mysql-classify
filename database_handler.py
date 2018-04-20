import pymysql
import os
import time
import math

EXIST_DEBUG_FLAG = 1

class Dictionary:
    type_tablename_dict = {
        'Picture': 'picture',
        'Video': 'video',
        'Music': 'music',
        'Document': 'document',
        'Other': 'other',
        'Folder':'folder'}
    type_dict = {
        'mp3': 'Music',
        'aac': 'Music',
        'flac': 'Music',
        'ogg': 'Music',
        'wma': 'Music',
        'm4a': 'Music',
        'aiff': 'Music',
        'wav': 'Music',
        'amr': 'Music',
        'flv': 'Video',
        'ogv': 'Video',
        'avi': 'Video',
        'mp4': 'Video',
        'mpg': 'Video',
        'mpeg': 'Video',
        '3gp': 'Video',
        'mkv': 'Video',
        'ts': 'Video',
        'webm': 'Video',
        'vob': 'Video',
        'wmv': 'Video',
        'png': 'Picture',
        'jpeg': 'Picture',
        'gif': 'Picture',
        'jpg': 'Picture',
        'bmp': 'Picture',
        'svg': 'Picture',
        'webp': 'Picture',
        'psd': 'Picture',
        'tiff': 'Picture',
        'txt': 'Document',
        'pdf': 'Document',
        'doc': 'Document',
        'docx': 'Document',
        'odf': 'Document',
        'xls': 'Document',
        'xlsv': 'Document',
        'xlsx': 'Document',
        'ppt': 'Document',
        'pptx': 'Document',
        'ppsx': 'Document',
        'odp': 'Document',
        'odt': 'Document',
        'ods': 'Document',
        'md': 'Document',
        'json': 'Document',
        'csv': 'Document'}

    def getTableName(self,type):
        """ Return type's table name """

        return self.type_tablename_dict[type]

    def getFileType(self,file_extension):
        """ Return file extension's type """

        if file_extension in self.type_dict:
            return self.type_dict[file_extension]
        else:
            return 'Other'

class SqlString:

    def __init__(self):
        """ Initial """

        self._dict= Dictionary()

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

        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,type VARCHAR(20) NOT NULL,name VARCHAR(100) NOT NULL,mtime DATETIME NOT NULL,size VARCHAR(20) NOT NULL,path VARCHAR(80) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def getCreateTypeTableStr(self, class_name):
        """ Return create type table SQL command """

        sql_str = "CREATE TABLE "
        sql_str += self._dict.getTableName(class_name)
        sql_str += "(id INT NOT NULL AUTO_INCREMENT,summary_id INT UNSIGNED NOT NULL,PRIMARY KEY (id));"
        return sql_str

    def getInsertTablesStr(self, path, file):
        """ Return Instert tables SQL command """

        path += "/"

        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        mtime = os.stat(path + file).st_mtime
        mtime2 = time.localtime(mtime)
        mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

        ## 5. type 1. name 2. mtime 3. size 4. path
        summary_sql = "INSERT INTO summary(type,name,mtime,size,path) VALUES(\""

        file_type = self._dict.getFileType(file_extension)

        summary_sql += file_type
        summary_sql += "\",\""
        summary_sql += file
        summary_sql += "\",STR_TO_DATE(\""
        summary_sql += mtime2_hr
        summary_sql += "\",\"%m/%d/%Y %T\"),\""
        summary_sql += self._convert_size(os.stat(path + file).st_size)
        summary_sql += "\", \""
        summary_sql += path
        summary_sql += "\") "

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

        path += "/"

        mtime = os.stat(path + folder).st_mtime
        mtime2 = time.localtime(mtime)
        mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

        summary_sql = "INSERT INTO summary(type,name,mtime,size,path) VALUES(\"Folder\",\""
        summary_sql += folder
        summary_sql += "\",STR_TO_DATE(\""
        summary_sql += mtime2_hr
        summary_sql += "\",\"%m/%d/%Y %T\"),\""
        summary_sql += self._convert_size(os.stat(path + folder).st_size)
        summary_sql += "\", \""
        summary_sql += path
        summary_sql += "\") "

        type_sql = "INSERT INTO folder"
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += folder
        type_sql += "\" AND path=\""
        type_sql += path
        type_sql += "\";"

        return summary_sql,type_sql


class DatabaseHandler:

    def __init__(self):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "root", "mydatabase")
        self._cursor = self._database.cursor()
        self._sql = SqlString()
        self._dict= Dictionary()

    def _sendSqlCmd(self,sql_str):
        """ Used to Send SQL Command """
        try:
            self._cursor.execute(sql_str)
            self._database.commit()
        except BaseException:
            # if (EXIST_DEBUG_FLAG == 1):
            #     print("Summary Table Already Exist")
            self._database.rollback()

    def createTables(self):
        """ Create summary table & type tables """

        # Create summary table
        sql_str = self._sql.getCreateSummaryTableStr()
        self._sendSqlCmd(sql_str)

        # Create Tables
        for index in self._dict.type_tablename_dict:
            # create each table
            class_sql_str = self._sql.getCreateTypeTableStr(index)
            self._sendSqlCmd(class_sql_str)

    def searchPath(self, path):
        """ Search path layer by layer to find files """

        fileList = os.listdir(path)
        for file in fileList:
            fullpath = os.path.join(path, file)
            if os.path.isdir(fullpath):
                folder = file
                # call insert
                self.insertFolderToTables(path,folder)
                self.searchPath(fullpath)
            elif os.path.isfile(fullpath):
                self.insertFileToTables(path, file)

    def insertFolderToTables(self,path,folder):
        """ Insert folder to tables """

        insert_summary_sql_str,insert_type_sql_str = self._sql.getInsertFolderStr(path, folder)

        self._sendSqlCmd(insert_summary_sql_str)
        self._sendSqlCmd(insert_type_sql_str)

    def insertFileToTables(self, path, file):
        """ Insert File to tables """

        insert_summary_sql_str,insert_type_sql_str = self._sql.getInsertTablesStr(path, file)

        self._sendSqlCmd(insert_summary_sql_str)
        self._sendSqlCmd(insert_type_sql_str)

    def checkPath(self, path):
        """ Start """

        self.createTables()
        self.searchPath(path)

    def clearAll(self):
        """ Clear all tables """

        self._sendSqlCmd("drop table document;")
        self._sendSqlCmd("drop table music;")
        self._sendSqlCmd("drop table other;")
        self._sendSqlCmd("drop table video;")
        self._sendSqlCmd("drop table summary;")
        self._sendSqlCmd("drop table picture;")
        self._sendSqlCmd("drop table folder;")


dd = DatabaseHandler()
dd.clearAll()
dd.checkPath("/home/apteam/Desktop/MySQLTestFiles")
print(" Done ! ")