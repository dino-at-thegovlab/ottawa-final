cd app
../bin -b 0.0.0.0:8000 -D --pid gunicorn.pid --error-logfile gunicorn-err.log noi_server:app