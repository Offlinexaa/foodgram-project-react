# Продуктовый помощник Foodgram

Сервис публикации рецептов. Позволяет подписвыаться на других авторов, формировать список избранных рецептов, добавлять рецепты в корзину и скачивать список ингредиентов, необходимых для приготовления рецептов из корзины.

### Деплой

Автоматически выполняется деплой на сервер в облаке Яндекса.

Статус: [![Deploy](https://github.com/Offlinexaa/foodgram-project-react/actions/workflows/build_and_deploy.yml/badge.svg)](https://github.com/Offlinexaa/foodgram-project-react/actions/workflows/build_and_deploy.yml)

### Как запустить проект:

Клонировать репозиторий и перейти в каталог infra в командной строке:

```
git clone https://github.com/Offlinexaa/foodgram-project-react.git
```

```
cd foodgram-project-react/infra/
```

Заполнить файл infra/.env (пример заполнения ниже). Для примера используется редактор nano:

```
nano .env
```

Добавить пользователя в группу docker или предоставить права суперпользователя.

```
usermod -a -G docker <current_user_name>
systemctl reload docker.service
```

Запустить проект:

```
up.sh
```

Будет выполнена проверка на отсутствие незаполненных переменных в .env. После проверки вам будет предложена возможность импортировать демонстрационный образец данных. После запуска контейнеров так же будет предложено создать учётную запись суперпользователя Django.

В демонстрационных данных имеется преднастроенный пользователь с реквизитами: username / email: admin / a@a.local

Проект доступен по ссылке:

```
http://localhost/ или http://<your_external_ip>/
```

### Импорт данных вручную

Для импорта демонстрационных данных воспользуйтесь командой

```
docker-compose exec backend python manage.py loaddata ./data/db.json
```

### Создание суперпользователя вручную

Для создания суперпользователя вручную воспользуйтесь командой

```
docker-compose exec backend python manage.py createsuperuser
```

### Требования и пример заполнения файла .env

Файл .env может содержать следующие переменные:
Обязательные:

```
ALLOWED_HOSTS - хосты с которых разрешен доступ к бэкенду
CSRF_TO - хосты (с протоколом), с которых разрешено управление авторизацией
DB_ENGINE - драйвер СУБД для Django
DB_HOST - имя хоста (docker-контейнера)
DB_NAME - имя базы данных для api_yamdb
DB_PORT - порт для подключения к базе данных
POSTGRES_PASSWORD - пароль пользователя из предыдущего пункта
POSTGRES_USER - имя пользователя, владельца базы данных или администратора СУБД
SECRET_KEY - секретный ключ для нужд Django
```

Опциональные:

```
DEBUG - режим работы сервера бэкенда (по умолчанию - False)
DJANGO_SUPERUSER_PASSWORD - пароль суперпользователей при создании без запроса ввода (по умолчанию - None)
```

Пример заполнения значениями по умолчанию:

```
ALLOWED_HOSTS=backend;<your_external_ip_or_Domain_name>
CSRF_TO=http://backend;http://<your_external_ip_or_Domain_name>
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PORT=5432
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
SECRET_KEY=Here_shoud_be_something_long_and_complex
```

### Документация доступна по ссылке:

```
http://localhost/api/docs/
```

### Требования:

Docker 20.10.14

docker-compose 1.25.0
