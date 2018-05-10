import os
import json
from PIL import Image
import pymysql

import dictionary
import sql_string

EXIST_DEBUG_FLAG = 1


class DatabaseHandler:
    """ Database handler only new once """

    def __init__(self):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "12345678", "mydatabase", charset="utf8")
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

    def _create_initial_table(self, user_name):
        """ Create summary & users table """
        # Create summary table
        sql_str = self._sql.get_create_summary_table_str()
        self._send_sql_cmd(sql_str)

        # Create users table
        sql_str = self._sql.get_create_user_table_str()
        self._send_sql_cmd(sql_str)

        # New user
        self._new_user(user_name)

    def _new_user(self, user_name):
        """ When new user get in, insert to users table & create user's file_type table """
        # Insert user to users table
        sql_str2 = self._sql.get_insert_user_table_str(user_name)
        self._send_sql_cmd(sql_str2)

        # Create (user)_(file_type) table
        self._create_user_type_table(user_name)

    def _create_user_type_table(self, user_name):
        """ Create (user)_(file_type) table """
        # Create Tables
        for file_type in self._dict.type_tablename_dict:
            # create each table
            type_sql_str = self._sql.get_create_type_table_str(user_name, file_type)
            self._send_sql_cmd(type_sql_str)

    def _insert_folder_to_tables(self, path, folder, user_name):
        """ Insert folder to tables """
        insert_summary_sql_str, insert_type_sql_str = \
            self._sql.get_insert_folder_str(path, folder, user_name)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

    def _set_thumbnail(self, path, file, user_name):
        """ Generate thumbnail """
        #  Generate thumbnail for image
        get_summary_id_sql = "SELECT id,type FROM summary WHERE name="
        get_summary_id_sql += file
        get_summary_id_sql += " AND path="
        get_summary_id_sql += path
        self._send_sql_cmd(get_summary_id_sql)

        summary_id = None
        file_type = ""
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            summary_id = row[0][0]
            file_type = row[0][1]

        self._database.commit()

        if file_type == 'image':
            full_path = os.path.join(path, file)
            img = Image.open(full_path)
            img.thumbnail((36, 36))
            save_str = "/Users/Terry/mysql_resize/"
            save_str += user_name

            # check dir
            if not os.path.isdir(save_str):
                os.mkdir(save_str)

            save_str += "/"
            save_str += str(summary_id)
            save_str += ".jpg"
            img.save(save_str)

    def _insert_file_to_tables(self, path, file, user_name):
        """ Insert File to tables """
        insert_summary_sql_str, insert_type_sql_str = \
            self._sql.get_insert_tables_str(path, file, user_name)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)
        self._set_thumbnail(path, file, user_name)

    def _check_path(self, path_or_file, user_name):
        """ When initial search path layer by layer to find files & add """
        if os.path.isdir(path_or_file):
            # input is a path
            path = path_or_file
            file_list = os.listdir(path)
            for file in file_list:
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    folder = file
                    # call insert
                    self._insert_folder_to_tables(path, folder, user_name)
                    self._check_path(full_path, user_name)
                elif os.path.isfile(full_path):
                    if not file.startswith('.'):
                        # '.' start file don't do
                        self._insert_file_to_tables(path, file, user_name)
        else:
            # input is a file
            path, file = os.path.split(path_or_file)
            if not file.startswith('.'):
                # '.' start file don't do
                self._insert_file_to_tables(path, file, user_name)

    def _get_json_payload(self, data, status=0, message='sucess'):
        """ Form defined format json payload """
        root = {}
        root['status'] = status
        root['message'] = message
        root['data'] = data
        return json.dumps(root)

    def initial_database_handler(self, path, user_name):
        """ Initial database handler : first time search path & create table """
        self._create_initial_table(user_name)
        self._check_path(path, user_name)

    def update_database_handler(self, path, user_name):
        """ Update new path or file """
        sql_str = self._sql.get_select_user_table_str()
        self._send_sql_cmd(sql_str)

        user_dict = []
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            user_dict.append(row[1])

        self._database.commit()

        # inside or not
        if user_name not in user_dict:
            self._new_user(user_name)

        # check path and insert files
        self._check_path(path, user_name)

    def clear_all(self):
        """ Clear all tables """
        sql_str = "SELECT * FROM users;"
        self._send_sql_cmd(sql_str)

        user_dict = []
        result = self._cursor.fetchall()
        for row in result:
            # row[1] = user
            user_dict.append(row[1])

        self._database.commit()

        for user in user_dict:
            for file_type in self._dict.type_tablename_dict:
                drop_sql = "DROP TABLE "
                drop_sql += user
                drop_sql += "_"
                drop_sql += file_type
                self._send_sql_cmd(drop_sql)

        self._send_sql_cmd("drop table summary;")
        self._send_sql_cmd("drop table users;")

    def get_user_type_table(self, user_name, file_type):
        """ Return user's (type) table with id """
        sql_str = self._sql.get_user_file_type_str(user_name, file_type)
        self._send_sql_cmd(sql_str)

        data_list = []
        result = self._cursor.fetchall()
        for row in result:
            temp = dict()
            temp['id'] = row[0]
            temp['file_name'] = row[1]
            temp['time'] = row[2]
            temp['type'] = file_type
            data_list.append(temp)

        self._database.commit()

        pack_data_list = dict()
        pack_data_list['list'] = data_list
        return self._get_json_payload(pack_data_list)

    def get_file_path_with_id(self, file_id):
        """ Return file's path with file id (summary table) """
        sql_str = self._sql.get_file_path_with_id_str(file_id)
        self._send_sql_cmd(sql_str)

        result = self._cursor.fetchall()

        return_path = result[0][0] + "/"
        return_path += result[0][1]

        self._database.commit()

        return return_path


# Example :

if __name__ == "__main__":
    dd = DatabaseHandler()

    # dd.clear_all()

    # #第一次進來
    # dd.initial_database_handler("/Users/Terry/Desktop/terry_dir", "terry")

    # #要更新家務的新路徑或檔案 # input folder id, file_name
    dd.update_database_handler("/Users/Terry/Desktop/testdog.jpg", "jack")

    # #取得某個user的type table json
    # print(dd.get_user_type_table('jack', 'file'))



    print(" Done ! ")
