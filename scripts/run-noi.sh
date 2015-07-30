#!/bin/bash -e


cd app

PGHOST=db PGUSER=postgres psql < network_of_innovators.sql
python network_of_innovators.py -b 0.0.0.0:8000 -D --pid gunicorn.pid --error-logfile gunicorn-err.log noi_server:app
