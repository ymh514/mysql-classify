from database import database_handler
import time
import os

if __name__ == "__main__":
    START_TIME = time.time()

    dd = database_handler.DatabaseHandler("/home/terry/Desktop/Nas/new_nas_env")

    # FIXME : update now retrun fake

    """
        make sure use check_nickename_in_database before update_database_handler
    """
    # dd.clear_all()

    # check exist
    # print(dd.check_nickname_in_database('5.jpg'))
    # if dd.check_nickname_in_database('5.jpg') == 0:
    #     print(dd.update_database_handler("5.jpg", "terry", "yx3111002030", "/somewhere/img", "auto",
    #                                      "IMG_20180516_181224.jpg"))
    # print(dd.update_database_handler("ncs8888.jpg", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.jpg"))
    print(dd.update_database_handler("6.flv", "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.mp4"))

    # # Input 'user','type' get table
    #print(dd.get_user_type_table('terry', 'image'))

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
