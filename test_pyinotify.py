import pyinotify
import os
from database import database_handler

class MyEventHandler(pyinotify.ProcessEvent):

    def __init__(self,watch_path):
        self._database_handler = database_handler.DatabaseHandler(watch_path)
        #self._database_handler.clear_all()

    def process_IN_CREATE(self, event):
        print ("CREATE event:", event.pathname)
        file_path = event.pathname

        if not os.path.isdir(file_path):
            path, file = os.path.split(file_path)
            self._database_handler.update_database_handler(file, "terry", "yx3111002030", "/somewhere/img", "auto","IMG_20180516_18ddd4.jpg")

    def process_IN_DELETE(self, event):
        print ("DELETE event:", event.pathname)
        file_path = event.pathname
        if not os.path.isdir(file_path):
            path, file = os.path.split(file_path)
            self._database_handler.delete_file_with_nickname(file)

    def process_IN_MODIFY(self, event):
        print ("MODIFY event:", event.pathname)


    def process_IN_MOVED_TO(self, event):
        print ("MOVED_TO event:", event.pathname)

    def process_IN_MOVED_FROM(self, event):
        print ("MOVED_FROM event:", event.pathname)

def main():
    # watch manager
    watch_path = '/home/terry/Desktop/Nas/new_nas_env/terry'
    wm = pyinotify.WatchManager()
    wm.add_watch(watch_path, pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = MyEventHandler(watch_path)

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()


if __name__ == '__main__':
    main()