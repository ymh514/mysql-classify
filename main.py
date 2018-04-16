import pymysql
import os
import math
import time


dict = {'mp3':'Music', 'aac':'Music', 'flac':'Music', 'ogg':'Music', 'wma':'Music', 'm4a':'Music', 'aiff':'Music', 'wav':'Music', 'amr':'Music',
        'flv':'Video','ogv':'Video', 'avi':'Video', 'mp4':'Video', 'mpg':'Video', 'mpeg':'Video', '3gp':'Video', 'mkv':'Video', 'ts':'Video', 'webm':'Video', 'vob':'Video', 'wmv':'Video',
        'png':'Picture', 'jpeg':'Picture', 'gif':'Picture', 'jpg':'Picture', 'bmp':'Picture', 'svg':'Picture', 'webp':'Picture', 'psd':'Picture', 'tiff':'Picture',
        'txt':'Document', 'pdf':'Document', 'doc':'Document', 'docx':'Document', 'odf':'Document', 'xls':'Document', 'xlsv':'Document', 'xlsx':'Document','ppt':'Document',
        'pptx':'Document', 'ppsx':'Document', 'odp':'Document', 'odt':'Document', 'ods':'Document', 'md':'Document', 'json':'Document', 'csv':'Document'
        };

slefTableDict = {'Picture':'picture','Video':'video','Music':'music','Document':'document'};

direction = "/"

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def doInDir(somedir,db):
    fileList = os.listdir(somedir)
    for f in fileList:
        fullpath = os.path.join(somedir, f)
        if os.path.isdir(fullpath):
            doInDir(fullpath,db)
        elif os.path.isfile(fullpath):
            insert(somedir, f,db)

def insert(somedir,f,db):

    somedir+="/"

    cursor = db.cursor()

    filename, file_extension = os.path.splitext(f)

    file_extension = file_extension.strip('.')

    mtime = os.stat(somedir + f).st_mtime
    mtime2 = time.localtime(mtime)
    mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

    if file_extension in dict:
        type = dict[file_extension]
    else:
        type = "DEFAULT"


    ## 1. name 2. mtime 3. size 4. path 5. type
    summarysql = "INSERT INTO summary VALUE(\""
    summarysql += f
    summarysql += "\",\""
    summarysql += mtime2_hr
    summarysql += "\",\""
    summarysql += convert_size(os.stat(somedir + f).st_size)
    summarysql += "\",\""
    summarysql += somedir
    summarysql += "\",\""
    summarysql += type
    summarysql += "\");"

    selfsql = "INSERT INTO "
    if type == 'DEFAULT':
        selfsql += "other"
    else:
        selfsql += slefTableDict[dict[file_extension]]
    selfsql += " VALUE(\""
    selfsql += f
    selfsql += "\",\""
    selfsql += mtime2_hr
    selfsql += "\",\""
    selfsql += convert_size(os.stat(somedir + f).st_size)
    selfsql += "\",\""
    selfsql += somedir
    selfsql += "\");"

    try:
        cursor.execute(summarysql)
        cursor.execute(selfsql)
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()


def main():
    db = pymysql.connect("localhost", "root", "root", "mydatabase")
    cursor = db.cursor()

    # create summary table
    create_summary_table_sql = "CREATE TABLE summary(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL,type VARCHAR(50) DEFAULT \"Other\");"
    create_picture_table_sql = "CREATE TABLE picture(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL);"
    create_music_table_sql = "CREATE TABLE music(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL);"
    create_video_table_sql = "CREATE TABLE video(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL);"
    create_document_table_sql = "CREATE TABLE document(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL);"
    create_other_table_sql = "CREATE TABLE other(name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL);"

    try:
        cursor.execute(create_summary_table_sql)
        cursor.execute(create_picture_table_sql)
        cursor.execute(create_music_table_sql)
        cursor.execute(create_video_table_sql)
        cursor.execute(create_document_table_sql)
        cursor.execute(create_other_table_sql)
        db.commit()
    except:
         print("Create part ERROR")


    # Insert files to summary & diff table
    doInDir(direction,db)

    db.close()


main()
