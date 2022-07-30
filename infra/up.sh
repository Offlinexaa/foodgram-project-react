#!/bin/bash

echo ' == Check necessary config files == '
if [ ! -f .env ]; then
    echo '.env file is necessary. Please create .env file.'
    echo 'For example of .env see README.md file.'
    exit 0
fi
echo 'File .env exists.'

echo ' == Running up containers == '
docker-compose up -d

read -p 'Import sample data? [y/n] (n): ' y

echo ' == Make and apply migrations == '
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

echo ' == Collecting static data == '
docker-compose exec backend python manage.py collectstatic --noinput

if [ $y = 'y' ] || [ $y = 'yes' ] || [ $y = 'Y' ] || [ $y = 'Yes' ] || [ $y = 'YES' ]
then
    echo ' == Importing sample data == '
    docker-compose exec backend python manage.py loaddata db.json
fi

read -p 'Create super user? [y/n] (n): ' s
if [ $s = 'y' ] || [ $s = 'yes' ] || [ $s = 'Y' ] || [ $s = 'Yes' ] || [ $s = 'YES' ]
then
    echo ' == Creating super user == '
    docker-compose exec backend python manage.py createsuperuser
fi

echo ' == Project Foodgram up an running =='
echo 'Now admin site acessible at http://localhost/admin/'
