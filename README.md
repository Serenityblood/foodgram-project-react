## Foodgram project react

[![Django-app workflow](https://github.com/Serenityblood/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Serenityblood/foodgram-project-react/actions/workflows/main.yml)

Адрес развёрнутого приложения:
```
http://foodgramserenity.ddns.net/
```
### Описание:
Проект Foodgram продуктовый помощник - платформа для публикации рецептов. 

### О проекте:
В этом сервисе пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления 
одного или нескольких выбранных блюд.

### Технологии:
- asgiref==3.2.10
- requests==2.26.0
- django==2.2.16
- djangorestframework==3.12.4
- PyJWT==2.1.0
- djangorestframework-simplejwt==4.8.0
- djoser==2.1.0
- django-filter==2.4.0
- psycopg2-binary==2.8.6
- Pillow==8.3.1
- drf-extra-fields==3.4.1
- simplejson==3.18.4
- gunicorn==20.0.4
- reportlab==3.6.6
### Начало

Клонирование проекта:
```
git clone https://github.com/serenityblood/foodgram-project-react.git
```
Для добавления файла .env с настройками базы данных на сервер необходимо:

* Установить соединение с сервером по протоколу ssh:
    ```
    ssh username@server_address
    ```
    Где username - имя пользователя, под которым будет выполнено подключение к серверу.
    
    server_address - IP-адрес сервера или доменное имя.
    
    Например:
    ```
    ssh praktikum@84.201.176.52
 
    ```
* На сервере создать файл .env

    ```
    touch .env
    ```

* Добавить настройки в файл .env:
    ```
    sudo nano .env
    ```
    Пример добавляемых настроек:
    ```
    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    DB_HOST=postgres
    DB_PORT=5432
    SECRET_KEY=ваш ключ
    DEBUG=False
    HOSTS=*
    SQLITE=False
    ```
* Добавить на сервер файлы docker-compose.yml, nginx.conf:
  их можно скопировать из проекта, склонированного на локальную машину
  ```
   scp /путь до репозитория/foodgram-project-react/infra/docker-compose.yml username@server_address:/home/username
  ```

Также необходимо добавить Action secrets в репозитории на GitHub в разделе settings -> Secrets:
* DOCKER_PASSWORD - пароль от DockerHub;
* DOCKER_USERNAME - имя пользователя на DockerHub;
* HOST - ip-адрес сервера;
* SSH_KEY - приватный ssh ключ (публичный должен быть на сервере);
* TELEGRAM_TO - id своего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
* TELEGRAM_TOKEN - токен бота (получить токен можно у @BotFather, /token, имя бота)
* DB_ENGINE=django.db.backends.postgresql
* DB_NAME = postgres
* POSTGRES_USER = postgres
* POSTGRES_PASSWORD = postgres
* DB_HOST = postgres
* DB_PORT = 5432
* SECRET_KEY - ваш ключ
* HOSTS = *
* DEBUG = False
* SQLITE = False
* USER - ваше имя на удаленном сервере

### Проверка работоспособности

Теперь если внести любые изменения в проект и выполнить:
```
git add .
git commit -m "..."
git push
```
Комманда git push является триггером workflow проекта.
При выполнении команды git push запустится набор блоков комманд jobs (см. файл yamdb_workflow.yaml).
Последовательно будут выполнены следующие блоки:
* tests - тестирование проекта на соответствие PEP8 и тестам pytest.
* build_and_push_to_docker_hub - при успешном прохождении тестов собирается образ (image) для docker контейнера 
и отправлятеся в DockerHub
* deploy - после отправки образа на DockerHub начинается деплой проекта на сервере.
Происходит копирование следующих файлов с репозитория на сервер:
  - docker-compose.yaml, необходимый для сборки трех контейнеров:
    + postgres - контейнер базы данных
    + backend - контейнер Django приложения + wsgi-сервер gunicorn
    + frontend - контейнер с файлами статики
    + nginx - веб-сервер
  
  После копировния происходит установка docker и docker-compose на сервере
  и начинается сборка и запуск контейнеров.
* send_message - после сборки и запуска контейнеров происходит отправка сообщения в 
  телеграм об успешном окончании workflow

После выполнения вышеуказанных процедур необходимо установить соединение с сервером:
```
ssh username@server_address
```
Отобразить список работающих контейнеров:
```
sudo docker container ls
```
В списке контейнеров копировать CONTAINER ID контейнера username/backend:(username - имя пользователя на DockerHub):
```
7e1f46a60555   nginx:1.19.3                   "/docker-entrypoint.…"   2 hours ago   Up 2 hours               0.0.0.0:80->80/tcp, :::80->80/tcp           serenity_nginx_1
63c744e4c0cf   serenityblood/foodgram_front:latest   "docker-entrypoint.s…"   2 hours ago   Exited (0) 2 hours ago                                               serenity_frontend_1
d1610b3b1ada   serenityblood/foodgram_back:latest    "gunicorn foodgram.w…"   2 hours ago   Up 2 hours               0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   serenity_backend_1
36acb2114524   postgres:13.0-alpine           "docker-entrypoint.s…"   2 hours ago   Up 2 hours               5432/tcp                                    serenity_db_1

```
Выполнить вход в контейнер:
```
sudo docker exec -it a47ce31d4b7b bash
```
Внутри контейнера выполнить миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Также можно наполнить базу данных начальными тестовыми данными:
```
python manage.py get_data
```
Для создания нового суперпользователя можно выполнить команду:
```
$ python manage.py createsuperuser
```
и далее указать: 
```
Email:
Username:
Password:
Password (again):
```
Собрать статические файлы в одну папку:
```
$ python manage.py collectstatic
```

Проект настроен, можно перейти в админ зону:
```
http://хост вашего сервера/admin
```
Или же перейти в сам проект:
```
http://хост вашего сервера/recipes
```

#### Примеры. Некоторые примеры запросов к API.

Запрос на получение списка рецептов:

```
http://хост вашего сервера/api/recipes
```

Запрос на получение списка пользователей
```
http://хост вашего сервера/api/users/
```

Для остановки и удаления контейнеров и образов на сервере:
```
sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q) && sudo docker rmi $(sudo docker images -q)
```
Для удаления volume базы данных:
```
sudo docker system prune -a
```

### Redoc

http://foodgramserenity.ddns.net/api/docs/redoc.html

### Автор

* **Бушланов Глеб** - [Serenityblood](https://github.com/serenityblood)