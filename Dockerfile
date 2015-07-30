#
# Network of Innovators Dockerfile for web
#
# https://github.com/govlab/ottawa-final
#

FROM debian:jessie
MAINTAINER John Krauss <john@thegovlab.org>

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get install -yqq python-pip libpq-dev python-dev python-gevent postgresql-client-9.4

WORKDIR noi

COPY . /noi/

RUN pip install -r /noi/requirements.txt
