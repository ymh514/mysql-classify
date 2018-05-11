from database import database_handler
import time

if __name__ == "__main__":
    START_TIME = time.time()

    dd = database_handler.DatabaseHandler()

    dd.clear_all()

    # #第一次進來
    dd.initial_database_handler("/Users/Terry/Desktop/terry_dir", "terry")

    # #要更新加入的新路徑或檔案 # input folder id, file_name
    # dd.update_database_handler("/Users/Terry/Desktop/jack_dir", "jack")

    # #取得某個user的type table json
    # print(dd.get_user_type_table('terry', 'image'))

    # #put id get file real path
    # print(dd.get_file_path_with_id(20))

    print("--- Done ! cost : %s seconds ---" % (time.time() - START_TIME))
