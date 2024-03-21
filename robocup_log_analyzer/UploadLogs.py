#!/usr/bin/python3

import glob
import os
import sys
import requests
import json
import zipfile
from hashlib import blake2s


TEMP_LOGS_FOLDER = "/tmp/robocup/logs/"
BASE_URL = ''


def main():
    if len(sys.argv) > 2:
        TEMP_LOG_FOLDER = sys.argv[2]
    # switch to log folder
    os.chdir(TEMP_LOGS_FOLDER)

    uname = os.uname()
    m = blake2s(digest_size=10)
    m.update(str.encode(str(uname)))
    logFilename = "loginfo_" + m.hexdigest() + ".txt"
    fd = os.open(logFilename, os.O_RDWR | os.O_CREAT)
    #fd = os.open(filename, os.O_APPEND | os.O_WRONLY | os.O_CREAT)
    os.write(fd, str.encode("\n\n\n\n### Upload ###"))
    os.write(fd, str.encode("TEMP_LOGS_FOLDER=" + str(TEMP_LOGS_FOLDER)))
    os.write(fd, str.encode("\n"))
    os.write(fd, str.encode("orig cwd=" + os.getcwd()))

    try:
        os.write(fd, str.encode("const cwd=" + os.getcwd()))
        if len(sys.argv) > 2:
            os.chdir(sys.argv[2])
            os.write(fd, str.encode("argv cwd=" + os.getcwd()))

        #Get list of interesting matches
        response = requests.get(BASE_URL + "/findInterestingMatches", verify=False)
        response_json = json.loads(response.text)

        # extract match IDs from response
        interesting_match_names = []
        for entry in response_json:
            interesting_match_names.append(entry)

        os.write(fd, str.encode("\n\n"))
        os.write(fd, str.encode("interesting_match_names: " + ", ".join(interesting_match_names)))
        os.write(fd, str.encode("\n\n"))

        print(interesting_match_names)

        # find all files in log folder
        for logfile in glob.glob("*.rcg"):
            filename = os.path.splitext(os.path.basename(logfile))[0]
            os.write(fd, str.encode(logfile + " - " + filename + "\n"))
            if filename in interesting_match_names:
                os.write(fd, str.encode("uploading: " + filename + ".{rcg,rcl}\n"))
                # post both logfiles to grails
                requests.post(url=BASE_URL+"/gameLogfiles", verify=False, files=get_zipped_payload(filename + ".zip", [filename + ".rcg", filename + ".rcl"]))
                
    except Exception as e:
        os.write(fd, str.encode(str(type(e))))
        os.write(fd, str.encode("\n"))
        os.write(fd, str.encode(str(e)))
        os.write(fd, str.encode("\n\n"))

    os.write(fd, str.encode("The End of Upload"))
    os.close(fd)

    requests.post(url=BASE_URL + "/scriptLogfiles", verify=False, files=get_payload([logFilename]))
    os.remove(logFilename)


def get_payload(filenames):
    files = []

    for f in filenames:
        files.append((f, open(f, 'rb')))

    return files

def get_zipped_payload(zipName, filenames):    
    files = []
    print("zipping" + zipName)
    with zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED) as zip:
        for f in filenames:
            print(f)
            zip.write(f)

    files.append((zipName, open(zipName, 'rb')))
    
    return files
    
    
if __name__ == "__main__":
    BASE_URL = sys.argv[1]
    
    if BASE_URL.endswith('/'):
        BASE_URL = BASE_URL + "robocup"
    else:
        BASE_URL = BASE_URL + "/robocup"

    if not (BASE_URL.startswith("https://") or BASE_URL.startswith("http://")):
        BASE_URL = "http://" + BASE_URL


    main()
