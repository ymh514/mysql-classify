import json
import os
import subprocess
import time
import shutil
import mutagen.id3
import mutagen.flac
import mutagen.mp4

from threading import Thread

import pymysql
from PIL import Image, ExifTags

from database.common_lib import sql_string, dictionary

EXIST_DEBUG_FLAG = 1


class DatabaseHandler:
    """ Database handler only new once """

    def __init__(self, home_path):
        """ Initial Class """

        self._database = pymysql.connect(
            "localhost", "root", "", "mydatabase", charset="utf8")
        self._cursor = self._database.cursor()

        self._sql = sql_string.SqlString(home_path)
        self._dict = dictionary.Dictionary()
        tmp_path = home_path + "/mysql_resize"
        # check dir
        if os.path.exists(home_path):
            if not os.path.isdir(tmp_path):
                os.mkdir(tmp_path)
        self._thumbnail_path = tmp_path
        self._face_ai_path = '/home/terry/Desktop/Nas/face/qimgserver'

    def testdb(self):
        self._cursor.execute('USE test_db;')

    def _send_sql_cmd(self, sql_str):
        """ Used to Send SQL Command """
        try:
            self._cursor.execute(sql_str)
            self._database.commit()
        except Exception as e:
            # print('-----')
            # print(e)
            # print(sql_str)
            # print('-----')
            return -1

    def clear_all(self):
        """ Reset database & Create summary & users table """
        # Reset database
        drop_str, create_str = self._sql.get_initial_str()
        self._send_sql_cmd(drop_str)
        self._send_sql_cmd(create_str)
        self._database.select_db("mydatabase")
        self._database.set_charset("utf8")

        # clear thumbnail path
        try:
            shutil.rmtree(self._thumbnail_path)
            os.mkdir(self._thumbnail_path)
        except:
            pass
            # print("not found thumbnail path")
        # Create summary table
        sql_str = self._sql.get_create_summary_table_str()
        self._send_sql_cmd(sql_str)

        # Create users table
        sql_str = self._sql.get_create_user_table_str()
        self._send_sql_cmd(sql_str)
        return self._get_json_payload()

    def _new_user(self, user_name):
        """ When new user get in, insert to users table & create user's file_type table """
        # Insert user to users table
        sql_str = self._sql.get_insert_user_table_str(user_name)
        self._send_sql_cmd(sql_str)

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
        # not use??
        insert_summary_sql_str, insert_type_sql_str = \
            self._sql.get_insert_folder_str(path, folder, user_name)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

    def _check_img_ready(self, path):
        try:
            Image.open(path)
            return 0
        except:
            return 1

    def _check_null(self,input_null):
        if input_null == 'NULL':
            return None
        else:
            return input_null

    def _set_thumbnail(self, file, user_name):
        """ Generate thumbnail """
        #  Generate thumbnail for image
        get_summary_id_sql = "SELECT id,type,nas_path FROM summary WHERE nickname=\""
        get_summary_id_sql += file
        get_summary_id_sql += "\";"

        self._send_sql_cmd(get_summary_id_sql)

        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()
            for row in result:
                # row[1] = user
                summary_id = row[0]
                file_type = row[1]
                nas_path = row[2]
            self._database.commit()

            if file_type == 'image':
                ######## face classify
                self.face_classify(nas_path, file, user_name)

                full_path = os.path.join(nas_path, file)
                image = Image.open(full_path)

                # prevent rotation
                try:
                    hasOrientation = False
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            hasOrientation = True
                            break
                    if hasOrientation:
                        try:
                            exif = image._getexif()
                        except Exception:
                            exif = None

                        if exif:
                            if exif[orientation] == 3:
                                image = image.rotate(180, expand=True)
                            elif exif[orientation] == 6:
                                image = image.rotate(270, expand=True)
                            elif exif[orientation] == 8:
                                image = image.rotate(90, expand=True)

                except (AttributeError, KeyError, IndexError):
                    # cases: image don't have getexif
                    pass
                image.thumbnail((256, 256))
                save_str = self._thumbnail_path + "/"
                save_str += user_name

                # check dir
                if not os.path.isdir(save_str):
                    os.mkdir(save_str)

                save_str += "/"
                save_str += str(summary_id)
                save_str += ".jpg"
                image.save(save_str)

                image.close()

            if file_type == 'video':
                full_path = os.path.join(nas_path, file)
                tmp_file_path = nas_path + '/'
                tmp_file_path += 'video_tmp.jpg'
                video_thumbnail_cmd = 'ffmpeg -i '
                video_thumbnail_cmd += full_path
                video_thumbnail_cmd += ' -ss 00:00:00 -vframes 1 '
                video_thumbnail_cmd += tmp_file_path
                p2 = subprocess.Popen([video_thumbnail_cmd, '-p'], shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)

                # make sure generate

                while self._check_img_ready(tmp_file_path):
                    pass  # do nothing

                image = Image.open(tmp_file_path)
                image.thumbnail((256, 256))
                save_str = self._thumbnail_path + "/"
                save_str += user_name

                # check dir
                if not os.path.isdir(save_str):
                    os.mkdir(save_str)

                save_str += "/"
                save_str += str(summary_id)
                save_str += ".jpg"
                image.save(save_str)

                # delete tmp img
                try:
                    os.remove(tmp_file_path)
                except:
                    pass

            if file_type == 'music':
                full_path = os.path.join(nas_path, file)

                save_str = self._thumbnail_path + "/"
                save_str += user_name

                # check dir
                if not os.path.isdir(save_str):
                    os.mkdir(save_str)

                save_str += "/"
                save_str += str(summary_id)
                save_str += ".jpg"

                no_cover_flag = 0

                try:
                    id3 = mutagen.id3.ID3(full_path)
                    open(save_str, 'wb').write(id3.getall('APIC')[0].data)
                except mutagen.id3.ID3NoHeaderError:
                    try:
                        flac = mutagen.flac.FLAC(full_path)
                        open(save_str, 'wb').write(flac.pictures[0].data)
                    except mutagen.flac.FLACNoHeaderError:
                        try:
                            mp4 = mutagen.mp4.MP4(full_path)
                            open(save_str, 'wb').write(mp4['covr'][0])
                        except:
                            no_cover_flag = 1

                if no_cover_flag == 1:
                    # copy
                    image = Image.open('database/album_art_empty.png')
                    save_str = self._thumbnail_path + "/"
                    save_str += user_name

                    # check dir
                    if not os.path.isdir(save_str):
                        os.mkdir(save_str)

                    save_str += "/"
                    save_str += str(summary_id)
                    save_str += ".jpg"
                    image.save(save_str)

                # delete tmp img
                try:
                    os.remove(tmp_file_path)
                except:
                    pass
        else:
            pass

    def _insert_file_to_tables(self, file_name, user_name, device_id, source_path, upload_mode, source_name=None):
        """ Insert File to tables, must be new in """
        if source_name is None:
            insert_summary_sql_str, insert_type_sql_str = \
                self._sql.get_insert_tables_str(file_name, user_name, device_id, source_path, upload_mode)
        else:
            insert_summary_sql_str, insert_type_sql_str = \
                self._sql.get_insert_tables_str(file_name, user_name, device_id, source_path, upload_mode, source_name)

        self._send_sql_cmd(insert_summary_sql_str)
        self._send_sql_cmd(insert_type_sql_str)

        self._set_thumbnail(file_name, user_name)

    def _check_path(self, file_name, user_name, device_id, source_path, upload_mode, source_name=None):
        """ When initial search path layer by layer to find files & add """

        # input is a file
        # path, file = os.path.split(path_or_file)
        if not file_name.startswith('.'):
            # '.' start file don't do
            if source_name is None:
                self._insert_file_to_tables(file_name, user_name, device_id, source_path, upload_mode)
            else:
                self._insert_file_to_tables(file_name, user_name, device_id, source_path, upload_mode, source_name)

    def _get_json_payload(self, path=None, data=None, status=0, message='sucess'):
        """ Form defined format json payload """
        root = {}
        root['status'] = status
        root['message'] = message
        if data is not None:
            root['data'] = data
        if path is not None:
            root['path'] = path
        return json.dumps(root)

    def update_database_handler(self, nickname, user_name, device_id, source_path, upload_mode, source_name=None):
        """ Update new path or file """
        exsist_flag = self._check_nickname_in_database(nickname)

        if exsist_flag == -1:
            return self._get_json_payload(status=-7, message='have same name in Nas')

        sql_str = self._sql.get_select_user_table_str()
        self._send_sql_cmd(sql_str)

        if self._cursor.rowcount > 0:
            user_dict = []
            result = self._cursor.fetchall()
            for row in result:
                # row[1] = user
                user_dict.append(row[1])

            self._database.commit()

            # inside or not
            if user_name not in user_dict:
                self._new_user(user_name)
        else:
            self._new_user(user_name)

        # check path and insert files
        if source_name is None:
            self._check_path(nickname, user_name, device_id, source_path, upload_mode)
        else:
            self._check_path(nickname, user_name, device_id, source_path, upload_mode, source_name)
        return self._get_json_payload()

    def get_user_type_table(self, user_name, file_type):
        """ Return user's (type) table with id """
        sql_str = self._sql.get_user_file_type_str(user_name, file_type)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        if self._cursor.rowcount > 0:
            # summary.id,type,nickname,nas_path,m_time,size,device_id,upload_mode
            data_list = []
            result = self._cursor.fetchall()
            # print(result)

            for row in result:
                temp = dict()
                temp['id'] = self._check_null(row[0])
                temp['type'] = self._check_null(row[1])
                temp['file_name'] = self._check_null(row[2])
                temp['nas_path'] = self._check_null(row[3])
                temp['m_time'] = self._check_null(row[4])
                temp['size'] = self._check_null(row[5])
                temp['device_id'] = self._check_null(row[6])
                temp['upload_mode'] = self._check_null(row[7])

                # # image return face_id
                if file_type == 'image':
                    image_info = dict()
                    image_info['latitude'] = self._check_null(row[8])
                    image_info['longitude'] = self._check_null(row[9])
                    image_info['city'] = self._check_null(row[10])
                    image_info['taken_time'] = self._check_null(row[11])
                    if row[12] is None:
                        image_info['face_id'] = -1
                    else:
                        image_info['face_id'] = self._check_null(row[12])

                    temp['image_info'] = image_info

                if file_type == 'video':
                    # # video return duration
                    video_info = dict()
                    video_info['duration'] = self._check_null(row[8])

                    temp['video_info'] = video_info

                if file_type == 'music':
                    music_info = dict()
                    music_info['title'] = self._check_null(row[8])
                    music_info['album'] = self._check_null(row[9])
                    music_info['artist'] = self._check_null(row[10])
                    music_info['duration'] = self._check_null(row[11])
                    music_info['samplerate'] = self._check_null(row[12])

                    temp['music_info'] = music_info

                data_list.append(temp)

            self._database.commit()

            pack_data_list = dict()
            pack_data_list['list'] = data_list
            return self._get_json_payload(data=pack_data_list)
        else:
            # message = file_type
            # message += ' is empty.'
            # return self._get_json_payload(message=message)
            return self._get_json_payload(status=-2000, message="The type table is empty in database.")

    def get_files_under_folder(self, folder_path):
        """ Return files under folder with id """
        sql_str = self._sql.get_files_under_folder_str(folder_path)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        if self._cursor.rowcount > 0:
            data_list = []
            result = self._cursor.fetchall()
            for row in result:
                temp = dict()
                temp['id'] = row[0]
                temp['type'] = row[1]
                temp['file_name'] = row[2]
                temp['nas_path'] = row[3]
                temp['m_time'] = row[4]
                temp['size'] = row[5]
                temp['device_id'] = row[6]
                temp['upload_mode'] = row[7]
                data_list.append(temp)

            self._database.commit()

            pack_data_list = dict()
            pack_data_list['list'] = data_list
            return self._get_json_payload(data=pack_data_list)
        else:
            return self._get_json_payload(status=-2000, message="Can't found in database.")

    def get_file_path_with_id(self, file_id):
        """ Return file's path with file id (summary table) """
        sql_str = self._sql.get_file_path_with_id_str(file_id)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()

            return_path = result[0][0] + "/"
            return_path += result[0][1]

            self._database.commit()
            return self._get_json_payload(path=return_path)
        else:
            return self._get_json_payload(status=-2000, message="Can't found in database.")

    def delete_file_with_id(self, file_id):
        """ Delete file with id """
        sql_str = self._sql.get_info_by_summaryid_str(file_id)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        # got thing
        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()
            user_name = result[0][0]
            file_type = result[0][1]

            user_table = user_name + '_'
            user_table += file_type

            delete_sql = self._sql.get_delete_summary_type_with_id_str(user_table, file_id)

            self._send_sql_cmd(delete_sql)

            # delete thumbnail
            thumbnail_path = self._thumbnail_path + '/'
            thumbnail_path += user_name
            thumbnail_path += '/'
            thumbnail_path += str(file_id)
            thumbnail_path += '.jpg'

            # print(thumbnail_path)
            try:
                os.remove(thumbnail_path)
            except:
                pass

            # change
            return self._get_json_payload()
        else:
            return self._get_json_payload(status=-2000, message="Can't found in database.")

    def rename_file_with_id(self, new_nickname, file_id):
        """ Update file in database with new file_path and id """
        sql_str = self._sql.get_info_by_summaryid_str(file_id)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        # got thing
        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()
            user_name = result[0][0]
            file_type = result[0][1]

            user_table = user_name + '_'
            user_table += file_type

            update_summary_sql_str, update_type_sql_str = self._sql.get_update_file_table_str(new_nickname,
                                                                                              user_name, file_id)
            self._send_sql_cmd(update_summary_sql_str)
            self._send_sql_cmd(update_type_sql_str)

            return self._get_json_payload()
        else:
            return self._get_json_payload(status=-2000, message="Can't found in database.")

    def get_image_thumbnail(self, image_id):
        """ Return image thumbnail with id """
        sql_str = self._sql.get_info_by_summaryid_str(image_id)
        catch_flag = self._send_sql_cmd(sql_str)

        if catch_flag == -1:
            # error
            return self._get_json_payload(status=-3000, message="The table isn't exist in database.")

        # got thing
        if self._cursor.rowcount > 0:
            result = self._cursor.fetchall()
            user_name = result[0][0]
            file_type = result[0][1]
            if not file_type == "image":
                return self._get_json_payload(status=-2100, message="there is no thumbnail for this type")
            thumbnail_path = self._thumbnail_path + "/"
            thumbnail_path += user_name
            thumbnail_path += "/"
            thumbnail_path += str(image_id)
            thumbnail_path += ".jpg"
            return self._get_json_payload(path=thumbnail_path)
        else:
            return self._get_json_payload(status=-2000, message="Can't found in database")

    def face_classify(self, path, file, user_name):

        """ set img """
        file_path = path + "/"
        file_path += file

        # TODO : path
        add_cmd = self._face_ai_path + '/'
        add_cmd += 'qimg add '
        add_cmd += file_path

        p = subprocess.Popen([add_cmd, '-p'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (stdoutput, erroutput) = p.communicate()

        info_cmd = self._face_ai_path + '/'
        info_cmd += 'qimg info '
        info_cmd += file_path

        get_id = '-1'
        # fetch 10 times
        for i in range(0, 5):
            p2 = subprocess.Popen([info_cmd, '-p'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (stdoutput2, erroutput) = p2.communicate()
            getgetget = stdoutput2.decode("utf-8")

            # if not number
            try:
                val = int(getgetget[0])
                if val != -1:
                    get_id = str(val)
                    # print("Found face : " + get_id)
            except ValueError:
                pass
                # print("Not found wait 1 second !")

            if get_id is not '-1':
                break
            # sleep 1 sec everytimes
            time.sleep(1)

        # update img table's id col
        if get_id is not '-1':
            # print("---------- Found face id : " + get_id + " ----------")
            type_sql = self._sql.get_face_id_update_str(file_path, user_name, get_id)
            self._send_sql_cmd(type_sql)
        else:
            pass
            # print('---------- Not found face id ----------')

    def _check_nickname_in_database(self, nickname):
        """ Private : Check nickname in database or not  """
        # exist return -1
        # not exist return 0

        check_sql = "SELECT * FROM summary WHERE nickname=\""
        check_sql += nickname
        check_sql += "\";"

        self._send_sql_cmd(check_sql)
        if self._cursor.rowcount > 0:
            return -1
        else:
            return 0

    def check_nickname_in_database(self, nickname):
        """ Check nickname in database or not  """
        # exist return -1
        # not exist return 0

        check_sql = "SELECT * FROM summary WHERE nickname=\""
        check_sql += nickname
        check_sql += "\";"

        self._send_sql_cmd(check_sql)
        if self._cursor.rowcount > 0:
            return self._get_json_payload(status=-7, message='Already have same name in Nas.')
        else:
            return self._get_json_payload()
