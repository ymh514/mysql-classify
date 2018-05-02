
import sys
import json
import subprocess

global inf 
def getNowTime():
    

    p=subprocess.Popen(["date","+%Y%m%d%H%M%S"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output,err = p.communicate()

    # POOL  = output[(output.find('pool:') +5): output.find('state:')]   

    inf = {"systemtime":output}
    n = json.dumps  (inf)
    jsonObj =json.loads(n)
    # return jsonObj
    return inf
