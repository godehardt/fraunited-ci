FROM ubuntu:22.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG DEBIAN_FRONTEND="noninteractive"
ARG DEBCONF_NOWARNINGS="yes"
ARG DEBCONF_TERSE="yes"

RUN apt-get update && apt-get -y upgrade && apt-get install -y apt-transport-https
RUN apt-get -y install unzip curl binutils g++ python3 python3-pip ruby build-essential git flex bison libboost-all-dev autoconf automake libtool iputils-ping

RUN mkdir -p /tmp/robocup/

RUN mkdir -p /tmp/rcssserver
RUN cd /tmp/rcssserver
RUN curl -L https://github.com/rcsoccersim/rcssserver/releases/download/rcssserver-18.1.3/rcssserver-18.1.3.tar.gz > /tmp/rcssserver/rcssserver-18.1.3.tar.gz
RUN tar xzvfp /tmp/rcssserver/rcssserver-18.1.3.tar.gz &&\
cd rcssserver-18.1.3 &&\
./configure &&\
make &&\
make install

COPY runRoboCupCI.sh /scripts/
RUN chmod +x /scripts/runRoboCupCI.sh

RUN pip3 install requests pyyaml

#RUN /scripts/runRoboCupCI.sh
CMD [ "/scripts/runRoboCupCI.sh" ]

