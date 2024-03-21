#!/usr/bin/python3

import requests
import json
import os
import sys
from configparser import ConfigParser, MissingSectionHeaderError
import traceback
from os.path import exists

BASE_URL = ""

def apply_configs(config_folder_path) :
    response = requests.get(BASE_URL + "/protocol/current", verify=False)
    response_json = json.loads(response.text)

    for config in response_json["configs"]:
        appy_config(config_folder_path, config)


# The original .conf files used for the FraUnited Team don't strictly follow the .ini or .conf syntax from what i can see.
# In detail they have 'loose' values at the start that would usually be in the [DEFAULT] section. However the files seem 
# to be working right now, so we play along and first add a [default] section in order to not get wrecked by a parsing error
# and then we remove the first line containing the section at the end. The result has the same structure as the input file. 
# This also removes all comments 
def appy_config(config_folder_path, config) :
    configParser = ConfigParser()

    fileName = config["fileName"]
    full_path = os.path.join(config_folder_path, fileName)

    if exists(full_path) == False:
        print("Config file <" + fileName + "> does not exist. Creating config ...")
        new_config = open(full_path, 'x')
        new_config.close()

    implicitIniFilePrefix = ""

    try:
        configParser.read(full_path)
    except MissingSectionHeaderError:
        implicitIniFilePrefix = "[default]\n"

    try:
        with open(full_path) as stream:
            configParser.read_string(implicitIniFilePrefix + stream.read())

        for configValue in config["entries"]:
            if(configValue["sectionName"]):
                if configValue["sectionName"] not in configParser.sections():
                    configParser.add_section(configValue["sectionName"])
                configParser.set(configValue["sectionName"], configValue["key"], configValue["value"])
            else:
                    configParser.set("default", configValue["key"], configValue["value"])


        configFile = open(full_path,'w')
        configParser.write(configFile)
        configFile.close()

        
        with open(full_path, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(full_path, 'w') as fout:
            fout.writelines(data[1:])
    except:
        print("Unable to write to config file: " + full_path + ". Error: " + traceback.format_exc())


if __name__ == "__main__":
    BASE_URL = sys.argv[1]
    if BASE_URL.endswith('/'):
        BASE_URL = BASE_URL + "api"
    else:
        BASE_URL = BASE_URL + "/api"

    if not (BASE_URL.startswith("https://") or BASE_URL.startswith("http://")):        
        BASE_URL = "http://" + BASE_URL

    config_folder_path = sys.argv[2]
    apply_configs(config_folder_path)
