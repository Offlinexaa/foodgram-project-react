#!/bin/bash

docker-compose stop
sleep 5
docker-compose rm -f backend
docker image rm infra_backend
docker-compose up -d
