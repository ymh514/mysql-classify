from database import database_handler
import time
import os

def travel_path(path,user_name):

    file_list = os.listdir(path)
    for file in file_list:
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            travel_path(full_path, user_name)
        elif os.path.isfile(full_path):
            if not file.startswith('.'):
                # '.' start file don't do
                print(dd.update_database_handler(file, user_name, "yx3111002030", '/fake/source/path', "manual","fake_sourcename.jpg"))


if __name__ == "__main__":
    START_TIME = time.time()

    dd = database_handler.DatabaseHandler("/home/terry/Desktop/Nas/new_nas_env")

    """
        make sure use check_nickename_in_database before update_database_handler
    """

    dd.clear_all()


    travel_path('/home/terry/Desktop/Nas/new_nas_env/terry','terry')


    # check exist
    # print(dd.check_nickname_in_database('5.jpg'))

    #print(dd.update_database_handler("ncs8888.jpg", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.jpg"))
    # print(dd.update_database_handler("01 飆高速 BIAOGAOSU 1.m4a", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.mp4"))
    # print(dd.update_database_handler("go_terry.wav", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.mp4"))
    # print(dd.update_database_handler("2.mp4", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.mp4"))

    # # Input 'user','type' get table
    # print(dd.get_user_type_table('terry', 'music'))

    # # Input 'id' get nas_path+file
    # print(dd.get_file_path_with_id(1))

    # # Input 'nas_path' get all file under the path : but it seems like useless cause all under one directory
    # print(dd.get_files_under_folder("/home/terry/Desktop/Nas/new_nas_env/terry"))

    # #Input 'id' get thumbnail path
    # print(dd.get_image_thumbnail(1))

    # print(dd.delete_file_with_id(1))

    # #rename
    #print(dd.rename_file_with_id('yo.jpg', 1))


    print("--- Done ! cost : %s seconds ---" % (time.time() - START_TIME))
