#TODO : update when file change

import os
import pymysql,math,time
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY

dict = {'mp3':'Music', 'aac':'Music', 'flac':'Music', 'ogg':'Music', 'wma':'Music', 'm4a':'Music', 'aiff':'Music', 'wav':'Music', 'amr':'Music',
        'flv':'Video','ogv':'Video', 'avi':'Video', 'mp4':'Video', 'mpg':'Video', 'mpeg':'Video', '3gp':'Video', 'mkv':'Video', 'ts':'Video', 'webm':'Video', 'vob':'Video', 'wmv':'Video',
        'png':'Picture', 'jpeg':'Picture', 'gif':'Picture', 'jpg':'Picture', 'bmp':'Picture', 'svg':'Picture', 'webp':'Picture', 'psd':'Picture', 'tiff':'Picture',
        'txt':'Document', 'pdf':'Document', 'doc':'Document', 'docx':'Document', 'odf':'Document', 'xls':'Document', 'xlsv':'Document', 'xlsx':'Document','ppt':'Document',
        'pptx':'Document', 'ppsx':'Document', 'odp':'Document', 'odt':'Document', 'ods':'Document', 'md':'Document', 'json':'Document', 'csv':'Document'
        };

classList = ['Picture','Video','Music','Document','Other']
slefTableDict = {'Picture':'picture','Video':'video','Music':'music','Document':'document','Other':'other'};


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


def createUpdate(path,name):
    path += "/"
    db = pymysql.connect("localhost", "root", "root", "mydatabase")
    cursor = db.cursor()
    filename, file_extension = os.path.splitext(name)

    file_extension = file_extension.strip('.')

    mtime = os.stat(path + name).st_mtime
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

    summarysql += name
    summarysql += "\",\""
    summarysql += mtime2_hr
    summarysql += "\",\""
    summarysql += convert_size(os.stat(path + name).st_size)
    summarysql += "\",\""
    summarysql += path
    summarysql += "\")"
    try:
        cursor.execute(summarysql)
        db.commit()
    except:
        # if errot occure
        db.rollback()

    select_sql = "SELECT * FROM summary WHERE name=\""
    select_sql += name
    select_sql += "\";"

    print(select_sql)

    try:
        cursor.execute(select_sql)
        results = cursor.fetchall()
        for row in results:
            id = row[0]

            sql = "INSERT INTO "

            tp = slefTableDict[dict[file_extension]]
            sql += tp
            sql += "(summary_id) VALUES("
            sql += str(id)
            sql += ");"
            print(sql)

            cursor.execute(sql)
        db.commit()

    except:
        print("Fetch Error")
        db.rollback()
    db.close()


def deleteUpdate():
    print()

def modifyUpdate():
    print()


class EventHandler(ProcessEvent):
    """ Event Handle """

    def process_IN_CREATE(self, event):
        if(event.name[0] != '.'):
            print("Create file: % s" % os.path.join(event.path, event.name))
            createUpdate(event.path,event.name)

    def process_IN_DELETE(self, event):
        if(event.name[0] != '.'):
            print("Deletefile: % s" % os.path.join(event.path, event.name))

    def process_IN_MODIFY(self, event):
        if(event.name[0] != '.'):
            print("Modifyfile: % s" % os.path.join(event.path, event.name))


def FSMonitor(path):
    wm = WatchManager()

    mask = IN_DELETE | IN_CREATE | IN_MODIFY

    notifier = Notifier(wm, EventHandler())

    wm.add_watch(path, mask, auto_add=True, rec=True)

    print('now starting monitor % s' % (path))


    while True:

        try:
            notifier.process_events()

            if notifier.check_events():

                notifier.read_events()

        except KeyboardInterrupt:

            notifier.stop()

            break

if __name__ == "__main__":
    FSMonitor('/home/apteam/Desktop/MySQLTestFiles')

