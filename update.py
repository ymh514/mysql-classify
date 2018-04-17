#TODO : update when file change

import os
import pymysql,math,time
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY

class SqlString:
    class_dict = {
        'Picture': 'picture',
        'Video': 'video',
        'Music': 'music',
        'Document': 'document',
        'Other': 'other'}
    type_dict = {
        'mp3': 'Music',
        'aac': 'Music',
        'flac': 'Music',
        'ogg': 'Music',
        'wma': 'Music',
        'm4a': 'Music',
        'aiff': 'Music',
        'wav': 'Music',
        'amr': 'Music',
        'flv': 'Video',
        'ogv': 'Video',
        'avi': 'Video',
        'mp4': 'Video',
        'mpg': 'Video',
        'mpeg': 'Video',
        '3gp': 'Video',
        'mkv': 'Video',
        'ts': 'Video',
        'webm': 'Video',
        'vob': 'Video',
        'wmv': 'Video',
        'png': 'Picture',
        'jpeg': 'Picture',
        'gif': 'Picture',
        'jpg': 'Picture',
        'bmp': 'Picture',
        'svg': 'Picture',
        'webp': 'Picture',
        'psd': 'Picture',
        'tiff': 'Picture',
        'txt': 'Document',
        'pdf': 'Document',
        'doc': 'Document',
        'docx': 'Document',
        'odf': 'Document',
        'xls': 'Document',
        'xlsv': 'Document',
        'xlsx': 'Document',
        'ppt': 'Document',
        'pptx': 'Document',
        'ppsx': 'Document',
        'odp': 'Document',
        'odt': 'Document',
        'ods': 'Document',
        'md': 'Document',
        'json': 'Document',
        'csv': 'Document'}

    def __init__(self):
        print()

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def getCreateSummaryTableStr(self):
        sql_str = "CREATE TABLE summary(id INT NOT NULL AUTO_INCREMENT,type VARCHAR(20) NOT NULL,name VARCHAR(100) NOT NULL,mtime DATETIME NOT NULL,size VARCHAR(20) NOT NULL,path VARCHAR(80) NOT NULL,PRIMARY KEY (id))"

        return sql_str

    def getCreateClassTableStr(self, class_name):
        sql_str = "CREATE TABLE "
        sql_str += self.class_dict[class_name]
        sql_str += "(id INT NOT NULL AUTO_INCREMENT,summary_id INT UNSIGNED NOT NULL,PRIMARY KEY (id));"
        return sql_str

    def getInsertSummaryTableStr(self, path, file):
        path += "/"

        filename, file_extension = os.path.splitext(file)

        file_extension = file_extension.strip('.')

        mtime = os.stat(path + file).st_mtime
        mtime2 = time.localtime(mtime)
        mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)

        ## 5. type 1. name 2. mtime 3. size 4. path
        summary_sql = "INSERT INTO summary(type,name,mtime,size,path) VALUES(\""


        if file_extension in self.type_dict:
            file_type = self.type_dict[file_extension]
        else:
            file_type = "Other"

        summary_sql += file_type
        summary_sql += "\",\""
        summary_sql += file
        summary_sql += "\",STR_TO_DATE(\""
        summary_sql += mtime2_hr
        summary_sql += "\",\"%m/%d/%Y %T\"),\""
        summary_sql += self.convert_size(os.stat(path + file).st_size)
        summary_sql += "\", \""
        summary_sql += path
        summary_sql += "\") "

        type_sql = "INSERT INTO "
        type_sql += self.class_dict[file_type]
        type_sql += "(summary_id) SELECT id FROM summary WHERE name=\""
        type_sql += file
        type_sql += "\";"

        return summary_sql,type_sql


_sql = SqlString()

def createUpdate(path,name):
    database = pymysql.connect("localhost", "root", "root", "mydatabase")
    cursor = database.cursor()

    insert_summary_sql_str,insert_type_sql_str = _sql.getInsertSummaryTableStr(path, name)
    try:
        cursor.execute(insert_summary_sql_str)
        cursor.execute(insert_type_sql_str)
        database.commit()
    except:
        # if errot occure
        database.rollback()


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

