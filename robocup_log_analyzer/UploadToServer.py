#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2023

from requests import post
import urllib3
import json
import re


def push_to_server(jsonData, commit_id):
    serveradress = "http://<servername>/api/match"

    key = ""
    source_code = jsonData  # json file muss direkt aus dem code kommen ohne es zwischen zu speichern
    print("commit_id: ", commit_id)
    print("source_data: ", source_code)

    # sending post request and saving response as response object
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # r = post(url=serveradress, verify=False, data=str(source_code))
    r = post(url=serveradress, json=jsonData)

    # extracting response text
    print("response: ", r.text)
    response_json = json.loads(r.text)
    return response_json["_id"]
    #print("The pastebin URL is:%s" % pastebin_url)

def get_commit_id():
    #TODO Textpfad muss angepasst werden
    file = open("/tmp/robocup/robocup_log_analyzer/commitid.txt", "r")

    commit_id = ""
    if file.mode == "r":
        commit_id = file.read().strip()
    return commit_id

def get_protocol_id():
    file = open("/tmp/robocup/protocolId.txt", "r")

    protocol_id = file.read().rstrip('\n')
    print("protocol_id: '" + str(protocol_id) + "'")

    return protocol_id
