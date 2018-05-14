from database import database_handler
import time
import os

if __name__ == "__main__":
    START_TIME = time.time()

    dd = database_handler.DatabaseHandler()

    # #第一次進來
    # dd.clear_all()
    # dd.initial_database_handler("/Users/Terry/Desktop/terry_dir", "terry")

    # dd.initial_database_handler("/Users/Terry/Desktop/terry_dir/img", "terry")
    # #要更新加入的新路徑或檔案 # input folder id, file_name
    # dd.update_database_handler("/Users/Terry/Desktop/terry_dir/ncs.jpg", "terry")

    # #取得某個user的type table json
    # print(dd.get_user_type_table('terry', 'image'))

    # #put id get file real path
    # print(dd.get_file_path_with_id(20))

    # #取得某路徑那層的所有file & folder
    # print(dd.get_files_under_folder("/Users/Terry/Desktop/terry_dir"))

    # #get thumbnail can only get image's thumbnail
    print(dd.get_image_thumbnail(3))

    print("--- Done ! cost : %s seconds ---" % (time.time() - START_TIME))

