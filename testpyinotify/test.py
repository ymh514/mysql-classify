import os
import time
from PIL import Image

from datetime import datetime


def get_date_taken(path):
    if Image.open(path)._getexif():
        return Image.open(path)._getexif()[36867]
    return None


dt_obj = datetime.strptime(get_date_taken("/Users/Terry/Desktop/MySQLFIles/ncs.jpg"),
                           '%Y:%m:%d %H:%M:%S')
millisec = dt_obj.timestamp() * 1000

print(millisec)

mtime = os.stat('/Users/Terry/Desktop/importC').st_mtime

c = 1523877875
m = 1525238703
a = 1525249043
cc = time.localtime(c)
mm = time.localtime(m)
aa = time.localtime(a)

ccc = time.strftime("%m/%d/%Y %H:%M:%S", cc)
mmm = time.strftime("%m/%d/%Y %H:%M:%S", mm)
aaa = time.strftime("%m/%d/%Y %H:%M:%S", aa)

print(ccc,mmm,aaa)
