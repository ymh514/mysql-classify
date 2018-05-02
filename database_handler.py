import pymysql
import os
import Dictionary
import SqlString
import json

EXIST_DEBUG_FLAG = 1

class DatabaseHandler:

    def __init__(self):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "12345678", "mydatabase")
        self._cursor = self._database.cursor()

        self._sql = SqlString.SqlString()
        self._dict= Dictionary.Dictionary()

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


        self._sendSqlCmd("drop table music;")
        self._sendSqlCmd("drop table file;")
        self._sendSqlCmd("drop table video;")
        self._sendSqlCmd("drop table summary;")
        self._sendSqlCmd("drop table image;")
        self._sendSqlCmd("drop table folder;")

    def getSummaryTable(self):

        get_summary_sql_str = self._sql.getSummaryTableStr()

        self._cursor.execute(get_summary_sql_str)

        return_dict = []
        result = self._cursor.fetchall()
        for row in result:
            tempdict = {}
            # print("1 : %s  2 : %s  3 : %s" % (row[1],row[2],row[3]))
            tempdict['type'] = row[1]
            tempdict['name'] = row[2]
            tempdict['path'] = row[3]

            return_dict.append(tempdict)

        self._database.commit()

        return json.dumps(return_dict)

    def getTypeTable(self,type):

        get_type_sql_str = self._sql.getTypeTableStr(type)

        self._cursor.execute(get_type_sql_str)

        return_dict = []
        result = self._cursor.fetchall()
        for row in result:
            tempdict = {}
            # print("1 : %s  2 : %s  3 : %s" % (row[1],row[2],row[3]))
            tempdict['type'] = row[1]
            tempdict['name'] = row[2]
            tempdict['path'] = row[3]

            return_dict.append(tempdict)

        self._database.commit()

        return json.dumps(return_dict)

    def getPathFiles(self,path):
        get_path_files_sql_str = self._sql.getPathFilesStr(path)
        self._cursor.execute(get_path_files_sql_str)

        return_dict = []
        result = self._cursor.fetchall()
        for row in result:
            tempdict = {}
            # print("1 : %s  2 : %s  3 : %s" % (row[1],row[2],row[3]))
            tempdict['type'] = row[1]
            tempdict['name'] = row[2]
            tempdict['path'] = row[3]

            return_dict.append(tempdict)

        self._database.commit()

        return json.dumps(return_dict)


dd = DatabaseHandler()
# dd.getPathFiles("/Volumes/YMH/MySQLTestFiles/audio")
# dd.clearAll()
# dd.checkPath("/Volumes/YMH/MySQLTestFiles")
# dd.getSummaryTable()
print(dd.getTypeTable("image"))
    # print(" Done ! ")