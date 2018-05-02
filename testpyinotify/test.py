import os
import time

mtime = os.stat('/Users/Terry/Desktop/importC').st_mtime
print(mtime)

#currenttimemillis
mtime2_hr = time.strftime("%m/%d/%Y %H:%M:%S", mtime2)
