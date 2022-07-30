docker-compose stop
Start-Sleep -Seconds 5
docker-compose rm -f backend
docker image rm infra_backend
docker-compose up -d