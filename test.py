import json


def _get_json_payload(data, status=0, message="sucess"):
    """ Form defined format json payload """
    root = {}
    root['status'] = status
    root['message'] = message
    root['data'] = data
    return json.dumps(root)


data_list = []

tempdict = {}
tempdict['file_name'] = 'a'
tempdict['id'] = 1
tempdict['type'] = 'image'
tempdict['time'] = 100
data_list.append(tempdict)

data = {}
data['list'] = data_list

#
# root = {}
# root['status'] = '-3000'
# root['message'] = 'sucess'
# root['data'] = data

print(_get_json_payload(data=data))
