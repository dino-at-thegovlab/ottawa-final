#
# Network of Innovators Dockerfile
#
# https://github.com/govlab/ottawa-final
#

FROM debian:jessie
MAINTAINER John Krauss <john@thegovlab.org>

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -yqq python-pip libpq-dev python-dev python-gevent

WORKDIR noi

COPY . /noi/

RUN pip install -r /noi/requirements.txt
