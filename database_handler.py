import os
import json
from PIL import Image
import pymysql

import dictionary
import sql_string

EXIST_DEBUG_FLAG = 1


class DatabaseHandler:

    def __init__(self):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "12345678", "mydatabase")
        self._cursor = self._database.cursor()

        self._sql = sql_string.SqlString()
        self._dict = dictionary.Dictionary()

    def _send_sql_cmd(self, sql_str):
        """ Used to Send SQL Command """
        try:
            self._cursor.execute(sql_str)
            self._database.commit()
        except BaseException:
            # if (EXIST_DEBUG_FLAG == 1):
            #     print("Summary Table Already Exist")
            self._database.rollback()

    def create_tables(self):
        """ Create summary table & type tables """
        # TODO : add username to table name

        # Create summary table
        sql_str = self._sql.get_create_summary_table_str()
        self._send_sql_cmd(sql_str)

        # Create Tables
        for file_type in self._dict.type_tablename_dict:
            # create each table
            class_sql_str = self._sql.get_create_type_table_str(file_type)
            self._send_sql_cmd(class_sql_str)

    def search_path(self, path):
        """ Search path layer by layer to find files """

        file_list = os.listdir(path)
        for file in file_list:
            full_path = os.path.join(path, file)
            if os.path.isdir(full_path):
                folder = file
                # call insert
                self.insert_folder_to_tables(path, folder)
                self.search_path(full_path)
            elif os.path.isfile(full_path):
                self.insert_file_to_tables(path, file)

    def insert_folder_to_tables(self, path, folder):
        """ Insert folder to tables """

        insert_summary_sql_str, insert_type_sql_str = self._sql.get_insert_folder_str(path, folder)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

    def insert_file_to_tables(self, path, file):
        """ Insert File to tables """

        insert_summary_sql_str, insert_type_sql_str = self._sql.get_insert_tables_str(path, file)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

    def check_path(self, path):
        """ Start """
        self.create_tables()
        self.search_path(path)

    def clear_all(self):
        """ Clear all tables """
        self._send_sql_cmd("drop table music;")
        self._send_sql_cmd("drop table file;")
        self._send_sql_cmd("drop table video;")
        self._send_sql_cmd("drop table summary;")
        self._send_sql_cmd("drop table image;")
        self._send_sql_cmd("drop table folder;")

    def get_summary_table(self):

        get_summary_sql_str = self._sql.get_summary_table_str()

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

    def get_type_table(self, file_type):

        get_type_sql_str = self._sql.get_summary_table_by_type_str(file_type)

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

    def get_path_files(self, path):
        get_path_files_sql_str = self._sql.get_path_files_str(path)
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

    def set_thumbnail(self):
        get_type_sql_str = self._sql.get_type_str('image')
        self._cursor.execute(get_type_sql_str)

        id_array = []
        result = self._cursor.fetchall()
        for row in result:
            id_array.append(row[1])
        self._database.commit()

        for summary_id in id_array:
            sql = "SELECT * FROM summary WHERE id="
            sql += str(summary_id)
            self._cursor.execute(sql)
            file_list = self._cursor.fetchall()
            for row in file_list:
                name = row[2]
                path = row[3]

                full_path = path + "/"
                full_path += name

                img = Image.open(full_path)
                img.thumbnail((36, 36))
                save_str = "/Users/Terry/mysql_resize/user1/"
                save_str += str(summary_id)
                save_str += ".jpg"
                img.save(save_str)
        self._database.commit()


dd = DatabaseHandler()
# dd.set_thumbnail()
# dd.get_path_files("/Volumes/YMH/MySQLTestFiles/audio")
dd.clear_all()
dd.check_path("/Users/Terry/Desktop/MySQLFIles")
# dd.get_summary_table()
# print(dd.get_type_table("image"))
print(" Done ! ")
