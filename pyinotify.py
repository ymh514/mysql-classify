import pyinotify
import os

class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_ACCESS(self, event):
        print ("ACCESS event:", event.pathname)

    def process_IN_ATTRIB(self, event):
        print ("ATTRIB event:", event.pathname)

    def process_IN_CLOSE_NOWRITE(self, event):
        print ("CLOSE_NOWRITE event:", event.pathname)

    def process_IN_CLOSE_WRITE(self, event):
        print ("CLOSE_WRITE event:", event.pathname)

    def process_IN_CREATE(self, event):
        print ("CREATE event:", event.pathname)

    def process_IN_DELETE(self, event):
        print ("DELETE event:", event.pathname)

    def process_IN_MODIFY(self, event):
        print ("MODIFY event:", event.pathname)

    def process_IN_OPEN(self, event):
        print ("OPEN event:", event.pathname)

def main():
    # watch manager
    wm = pyinotify.WatchManager()
    wm.add_watch('/home/apteam/Desktop/MySQLTestFiles', pyinotify.ALL_EVENTS, rec=True)

    # event handler
    eh = MyEventHandler()

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()



    # wm = pyinotify.WatchManager()
    # notifier = pyinotify.Notifier(wm)
    # wm.add_watch('/home/Desktop/MySQLTestFiles', pyinotify.IN_CLOSE_WRITE, rec=True,
    #              auto_add=True, proc_fun=MyEventHandler())
    # notifier.loop(daemonize=False, callback=None)


if __name__ == '__main__':
    main()