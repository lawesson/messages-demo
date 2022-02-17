#!/bin/bash

PYTHONPATH=${PYTHONPATH}:$(pwd)
export PYTHONPATH

if [[ "$1" == "migrate" ]]; then
  #  Quick and dirty hack to mitigate startup problems when we need to wait for the database to start
  RETRIES=10
  while ! ./manage.py migrate 2>/dev/null; do
    RETRIES=$((RETRIES - 1))
    if [[ ${RETRIES} -lt 0 ]]; then
      echo "Gave up after too many retries"
      exit 10
    fi
    echo "Failed to migrate but will retry ${RETRIES} more times (maybe db is booting)"
    sleep 1
  done
elif [[ "$1" == "test" ]]; then
  ./manage.py test
elif [[ "$1" == "run" ]]; then
  exec gunicorn -c docker/gunicorn_cfg.py main.wsgi
else
  exec "$@"  # To allow any other command sequence to be run conveniently
fi
