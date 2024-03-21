#!/bin/bash
#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2024
set -e

LD_LIBRARY_PATH=/usr/local/lib
export LD_LIBRARY_PATH

certificate='--insecure'
CURL="curl -s ${certificate}"

backend=''
rootDir='/tmp/robocup'
teamsFolder="${rootDir}/hlm/teams"
analyzerLogFolder="${rootDir}/logs"
logAnalyzerBinFolder="${rootDir}/robocup_log_analyzer"
tournamentFolder="${rootDir}/hlm/tournament"
hlmLogFolder="${tournamentFolder}/log"

debugLogFileName='debugLog.txt'
commitIdFileName='commitid.txt'
teamnamesFileName='teamnames.txt'
hlmConfigFileName='infRobocupCi.yml'
protocolIdFileName='protocolId.txt'
commitIdFile="${logAnalyzerBinFolder}/${commitIdFileName}"
teamnamesFile="${teamsFolder}/${teamnamesFileName}"
hlmConfigFile="${tournamentFolder}/${hlmConfigFileName}"
fraUnitedConfFolder='agent/conf'
debugLogFile="${rootDir}/${debugLogFileName}"
protocolIdFile="${rootDir}/${protocolIdFileName}"

gitlabToken='TOKEN'
gitlab='<sername>'
jobName='build-job-ubuntu-20.04'

debug() {
    echo $1
    echo $1 >> $debugLogFile
}

currentDate=`date`
echo 'Creating empty log file ...'
echo 'DEBUG LOG' > $debugLogFile
echo $currentDate >> $debugLogFile
echo '#################################################' >> $debugLogFile

backendArg=$1

if [ -z "${backendArg}" ]; then
    backend='<servername>'
    debug "Talking to prod backend: ${backend}"
else
    backend="${backendArg}"
    debug "Talking to dev backend: ${backend}"
fi

step() {
    echo "step: $@" | sed 'p; s/./=/g' >> $debugLogFile
}

processTeams() {
    teamname=$1
    teamFolderPath="${teamsFolder}/${teamname}"
    teamSetupScriptPath="${teamFolderPath}.sh"
    teamZipPath="${teamFolderPath}.zip"

    echo process team $teamname
    echo $teamFolderPath
    echo $teamSetupScriptPath
    echo $teamZipPath

    if [ -d "$teamFolderPath" ]; then
        rm -Rf $teamFolderPath;
    fi

    debug "Fetching <${teamname}> ..."



    if [ $teamname == 'FRA-UNIted-LATEST' ]; then
        debug "Fetching latest gitlab artifact (team binary) ..."
        $CURL "$gitlab/api/v4/projects/376/jobs/artifacts/master/download?job=$jobName" $certificate -o $teamZipPath --header "Private-TOKEN: $gitlabToken"

        debug "Unpacking <${teamname}> ..."
        unzip -oq $teamZipPath -d $teamFolderPath
        debug "Extracting commitIdFile"
        mv $teamFolderPath/commitid.txt $commitIdFile

    else
        # We no longer have the commit id as top level node, so in the case that we are running fixed teams we don't have a commit id.
        if [ -e $commitIdFile ]; then
            debug "Using existing CommitId file ..."
        else
            debug "CommitId not found. Creating default ..."
            echo "No CommitId file found. Creating default ..."
            echo ">-1<" > $commitIdFile
        fi;
    
        $CURL "${backend}/api/team/${teamname}/zip" -o $teamZipPath
        debug "Unpacking <${teamname}> ..."
        unzip -oq $teamZipPath -d $teamFolderPath

        debug "Cleaning up <${teamname}> ..."
        rm $teamZipPath
    fi;

    debug "Setting access permissions for <${teamname}> ..."
    chmod a+x -R $teamFolderPath


    if [ -e "${teamFolderPath}/team.yml" ]; then
        debug "team.yml exists"
    else
        debug "team.yml not found. Creating default ..."
        debug "name: ${teamname}" > "${teamFolderPath}/team.yml"
        debug "country: germany" >> "${teamFolderPath}/team.yml"
    fi;

    sed -i 's/\r//' "${teamFolderPath}/start"
    sed -i 's/\r//' "${teamFolderPath}/kill"

    if [[ $teamname == 'FRA-UNIted' || $teamname == 'FRA-UNIted-LATEST' ]]; then
        cd $rootDir
        debug "Writing custom config values ..."
        chmod a+x ./ConfigHandler.py
        ./ConfigHandler.py $backend "${teamFolderPath}/${fraUnitedConfFolder}"
        debug "Custom config values done"
    fi

    setupScriptResponseCode="$($CURL "${backend}/api/team/${teamname}/sh" -o $teamSetupScriptPath -s -w "%{http_code}")"
    if [ $setupScriptResponseCode = 200 ]; then
        echo "Setup script found for ${teamname}"
        chmod a+x $teamSetupScriptPath

        $teamSetupScriptPath $teamFolderPath $teamname
    fi;

    debug "<${teamname}> done"
}

step initialize 
(   
    echo "Removing previous commitId file ..."
    rm -f $commitIdFile

    chmod a+x "${tournamentFolder}/ssh-off.sh"
    chmod a+x "${tournamentFolder}/ssh-on.sh"
    chmod a+x "${tournamentFolder}/start.sh"
    chmod a+x "${tournamentFolder}/sync.sh"
    chmod a+x "${tournamentFolder}/test-team.sh"

    chmod a+x "${rootDir}/ConfigHandler.py"
)

step fetch hlm config from Jenkins
(
    echo "load protocol config from backend"
    $CURL "${backend}/api/protocol/current/yaml" -L -o $hlmConfigFile
)

step fetch current protocol id 
(
    $CURL $certificate "$backend/api/protocol/current/id" -L > $protocolIdFile
)

step fetch teams
(
    echo "load teams from backend"
    rm -rf $teamsFolder
    mkdir $teamsFolder
    $CURL "${backend}/api/protocol/current/teams" -L -o $teamnamesFile

    # Transform json array of string into rows of teamnames
    sed -i 's/\[//g' $teamnamesFile
    sed -i 's/\]//g' $teamnamesFile
    sed -i 's/\"//g' $teamnamesFile
    sed -i 's/,/\n/g' $teamnamesFile
    # We add another new line so the while loop later catches the last row
    sed -i '$a\' $teamnamesFile

    while read name; do
        processTeams $name
    done <$teamnamesFile

    debug "Teams done"
)

step create log folder
(
    rm -rf $hlmLogFolder
    rm -rf $analyzerLogFolder
    cd $logAnalyzerBinFolder && chmod a+x RoboCup_main.py
    mkdir $analyzerLogFolder
)

step run matches
(
    debug 'Starting matches ...'
    cd $tournamentFolder
    # FIXME should be omitted in the first place when genereating the yaml config file
    sed --in-place "/^protocol_id/d" ${hlmConfigFileName}
    ./start.sh --config="${hlmConfigFileName}" >> $debugLogFile
)

#step upload interesting matches
#(
#    sleep 10m
#    cd $logAnalyzerBinFolder
#    chmod a+x UploadLogs.py
#    ./UploadLogs.py $backend "${analyzerLogFolder}/"
#)

step upload script logs
(
    $CURL $certificate -F "scriptPrints=@${debugLogFile}" "${jenkins}/robocup/scriptLogfile"
)
