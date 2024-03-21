#!/bin/bash
#         .-._
#       .-| | |
#     _ | | | |__FRANKFURT
#   ((__| | | | UNIVERSITY
#      OF APPLIED SCIENCES
#
#   (c) 2022-2024

rmdir -rf /tmp/robocup
mkdir -p /tmp/robocup

cd /tmp/robocup
curl --insecure https://<servername>/Dockerfile > /tmp/robocup/Dockerfile
curl --insecure https://<servername>/runRoboCupCI.sh > /tmp/robocup/runRoboCupCI.sh

docker build -t robocup:1.2 .
docker run --uts=host --detach robocup:1.2
