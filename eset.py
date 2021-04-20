import requests
import json
import os
import time

EEI_URL = "https://192.168.133.7:8443"
AUTH_PAYLOAD = {"domain":None,"username":"username","password":"password"}

def auth():
    response = requests.put("{}/api/v1/authenticate".format(EEI_URL),json=AUTH_PAYLOAD,verify=False)
    return response.headers["X-Security-Token"]


def download(processID):
    BEARER_HEADER = {"Authorization" : "Bearer {}".format(auth())} 
    response = requests.get("{}/frontend/download/start/{}".format(EEI_URL,processID),headers=BEARER_HEADER,verify=False)
    uuid = json.loads(response.text)["uuid"]
    name = json.loads(response.text)["name"]
    password = json.loads(response.text)["password"]
    name = os.path.splitext(name)[0] + ".zip"
    while True:
        response = json.loads(requests.post("{}/frontend/download/status".format(EEI_URL,processID),json={"uuid":uuid},headers=BEARER_HEADER,verify=False).text)["status"]
        time.sleep(0.5)
        if response == "FileReady":
            break
    response = requests.get("{}/download/{}/{}".format(EEI_URL,uuid,name),headers=BEARER_HEADER,verify=False)
    open(name,"wb").write(response.content)

def hash_block(hashes:list,comment = "",clean=False):
    BEARER_HEADER = {"Authorization" : "Bearer {}".format(auth())} 
    response = requests.put("{}/frontend/hashes/block".format(EEI_URL),headers=BEARER_HEADER,json={"comment":comment,"sha1":hashes,"shouldClean":clean},verify=False)
    return response.status_code

# def hash_unblock(processids:list)

def list_client():
    BEARER_HEADER = {"Authorization" : "Bearer {}".format(auth())} 
    payload = json.loads(open("list.txt").read())
    response = requests.post("{}/frontend/machines/1/0".format(EEI_URL),json=payload,headers=BEARER_HEADER,verify=False)
    return response.text
    
def client_shell(client_id,command="ipconfig"):
    BEARER_HEADER = {"Authorization" : "Bearer {}".format(auth()),"Referer":"{}/console/machines/{}/terminal".format(EEI_URL,client_id)} 
    response = requests.post("{}/frontend/machines/{}/shell/connect".format(EEI_URL,str(client_id)),json=AUTH_PAYLOAD,headers=BEARER_HEADER,verify=False)
    counter = 0
    out = []
    if json.loads(response.text)["connected"] == True:
        last_idx = json.loads(response.text)["lastIdx"]
        #
        command = requests.post("{}/frontend/machines/{}/shell/command".format(EEI_URL,client_id),json={"command":command},headers=BEARER_HEADER,verify=False)
        output = requests.post("{}/frontend/machines/{}/shell/output".format(EEI_URL,client_id),json={"lastIdx":last_idx},headers=BEARER_HEADER,verify=False)
        out.append(output.text)
        output = requests.post("{}/frontend/machines/{}/shell/output".format(EEI_URL,client_id),json={"lastIdx":last_idx},headers=BEARER_HEADER,verify=False)
        out.append(output.text)
        return out

print(client_shell(4))
