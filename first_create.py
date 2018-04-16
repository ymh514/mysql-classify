import pymysql
import os
import math
import time


#TODO : update when file change

dict = {'mp3':'Music', 'aac':'Music', 'flac':'Music', 'ogg':'Music', 'wma':'Music', 'm4a':'Music', 'aiff':'Music', 'wav':'Music', 'amr':'Music',
        'flv':'Video','ogv':'Video', 'avi':'Video', 'mp4':'Video', 'mpg':'Video', 'mpeg':'Video', '3gp':'Video', 'mkv':'Video', 'ts':'Video', 'webm':'Video', 'vob':'Video', 'wmv':'Video',
        'png':'Picture', 'jpeg':'Picture', 'gif':'Picture', 'jpg':'Picture', 'bmp':'Picture', 'svg':'Picture', 'webp':'Picture', 'psd':'Picture', 'tiff':'Picture',
        'txt':'Document', 'pdf':'Document', 'doc':'Document', 'docx':'Document', 'odf':'Document', 'xls':'Document', 'xlsv':'Document', 'xlsx':'Document','ppt':'Document',
        'pptx':'Document', 'ppsx':'Document', 'odp':'Document', 'odt':'Document', 'ods':'Document', 'md':'Document', 'json':'Document', 'csv':'Document'
        };

classList = ['Picture','Video','Music','Document','Other']
slefTableDict = {'Picture':'picture','Video':'video','Music':'music','Document':'document','Other':'other'};


direction = "/home/apteam/Desktop/MySQLTestFiles"

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def summary(somedir,db):
    fileList = os.listdir(somedir)
    for f in fileList:
        fullpath = os.path.join(somedir, f)
        if os.path.isdir(fullpath):
            summary(fullpath,db)
        elif os.path.isfile(fullpath):
            insert_to_summary(somedir, f,db)

def insert_to_summary(somedir,f,db):

    somedir+="/"

    cursor = db.cursor()

    filename, file_extension = os.path.splitext(f)

    file_extension = file_extension.strip('.')

    mtime = os.stat(somedir + f).st_mtime
    mtime2 = time.localtime(mtime)
    mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

    summarysql = ""
    ## 5. type 1. name 2. mtime 3. size 4. path
    if file_extension in dict:
        summarysql = "INSERT INTO summary(type,name,mtime,size,path) VALUES(\""
        type = dict[file_extension]
        summarysql += type
        summarysql += "\",\""

    else:
        summarysql = "INSERT INTO summary(name,mtime,size,path) VALUES(\""

    summarysql += f
    summarysql += "\",\""
    summarysql += mtime2_hr
    summarysql += "\",\""
    summarysql += convert_size(os.stat(somedir + f).st_size)
    summarysql += "\",\""
    summarysql += somedir
    summarysql += "\")"

    try:
        cursor.execute(summarysql)
        db.commit()
    except:
        # if errot occure
        db.rollback()

def classify(db):
    db = pymysql.connect("localhost", "root", "root", "mydatabase")

    cursor = db.cursor()



    # Create Tables
    for index in classList:
        # create each table
        create_table_sql = "CREATE TABLE "
        create_table_sql += slefTableDict[index]
        create_table_sql += "(id int NOT NULL AUTO_INCREMENT,summary_id INT UNSIGNED NOT NULL,PRIMARY KEY (id));"

        try:
            cursor.execute(create_table_sql)
            db.commit()
        except:
            print("Exist")
            db.rollback()

    # Select & insert
    for index in classList:
        select_sql = "SELECT * FROM summary WHERE type=\""
        select_sql += index
        select_sql += "\";"

        try:
            cursor.execute(select_sql)
            results = cursor.fetchall()
            for row in results:
                id = row[0]
                sql = "INSERT INTO "

                tp = slefTableDict[index]
                sql += tp
                sql += "(summary_id) VALUES("
                sql += str(id)
                sql += ");"

                cursor.execute(sql)
            db.commit()

        except:
            print("Fetch Error")
            db.rollback()




def main():
    db = pymysql.connect("localhost", "root", "root", "mydatabase")
    cursor = db.cursor()

    # create summary table
    create_summary_table_sql = "CREATE TABLE summary(id int NOT NULL AUTO_INCREMENT,type VARCHAR(50) DEFAULT \"Other\",name VARCHAR(50) NOT NULL,mtime VARCHAR(50) NOT NULL,size VARCHAR(50) NOT NULL,path VARCHAR(50) NOT NULL,PRIMARY KEY (id))"

    try:
        cursor.execute(create_summary_table_sql)
        db.commit()
    except:
         print("Exist")


    # Insert files to summary
    summary(direction,db)

    # classify from summary
    classify(db)

    db.close()

main()
