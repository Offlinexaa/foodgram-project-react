#!/bin/bash

docker-compose stop
sleep 5
docker-compose rm -f backend
docker image rm infra_backend
docker-compose up -d
# sleep 5
# docker-compose exec backend python manage.py createsuperuser --username admin --email a@a.local --noinput
# docker-compose exec backend python manage.py load_data