#!/bin/bash
#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2021-2024
set -e

step() {
    echo "step: $@" | sed 'p; s/./=/g'
}

# start script
# ============

step pull latest version and jump into that
(
    echo "clean up tmp..."
    rm -rf /tmp/robocup

    echo "stepping into tmp..."
    cd /tmp
#    should not work anymore as home directory not mounted in case of cronjob
#    git clone git@gitlab.informatik.fb2.hs-intern.de:godehardt/robocup-ci.git robocup
    echo "cloning repo..."
    git clone --verbose git@github.com:godehardt/fraunited-ci.git robocup
    echo "chmod hlm start script..."
    chmod a+x /tmp/robocup/runHLM.sh
    echo "initiating real script..."
	/tmp/robocup/runHLM.sh 
)
