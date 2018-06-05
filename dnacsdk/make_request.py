from dnacsdk.auth_service import get_auth_params
import requests
import pprint

def get_req(path):
    dnaObj={}
    dnaObj = get_auth_params()
    token = dnaObj['token']
    ipAddr = dnaObj['ip']
    print("Token is:"+str(token))
    print("IP is:" + str(ipAddr))

    headers = {'x-auth-token': token, 'Content-type': 'application/json'}
    req_Get_Dev = requests.get('https://'+ipAddr+path, verify=False,
                              headers=headers, stream=True)
    status = req_Get_Dev.status_code
    data = req_Get_Dev.json()
    #print(str(data))
    return data

#get_req('/api/v1/network-device')
