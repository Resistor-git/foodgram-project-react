# YourRecipes
#### YourRecipes - это проект позволяющий создавать рецепты и публиковать их.

YourRecipes имеет несколько ключевых особенностей, включая:

- Список избранных рецептов.
- Подписка на авторов.
- Возможность скачать список всех ингредиентов из выбранных рецептов для удобства при покупке.

Неавторизованным пользователям доступны для просмотра все рецепты.
Для создания собственного рецепта, добавления рецепта в избранное и подписки на авторов требуется регистрация.

## Документация к API
Чтобы ознакомиться с документацией и возможными запросами к API запустите сервер локально и перейдите по ссылке: http://127.0.0.1/api/docs/

## Как запустить проект локально (только бекэнд)
Клонировать репозиторий:

`https://github.com/Resistor-git/your_recipes.git`

Перейти в репозиторий в командной строке:

`cd your_recipes`

Создать и активировать виртуальное окружение:

Linux `python3 -m venv venv`

Windows `py -m venv venv`

Установить зависимости из requirements.txt:

Linux

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Windows
```
py -m pip install --upgrade pip
pip install -r requirements.txt
```

В папке с файлом manage.py выполнить миграции и запустить проект:
Lunix
```
python3 manage.py migrate
python3 manage.py runserver
```
Windows
```
py manage.py migrate
py manage.py runserver
```

## Запуск локально в контейнерах Docker
Установите и запустите [Docker](https://www.docker.com/products/docker-desktop/)

Создайте в корне проекта файл .env и заполните его следующими данными:
* POSTGRES_DB=your_recipes
* POSTGRES_USER=your_recipes_user
* POSTGRES_PASSWORD=пароль от базы данных на ваш выбор
* DB_HOST=db
* DB_PORT=5432
* SECRET_KEY=секретный клюл для Django

Перейдите в консоли папку /infra

`cd infra`

Запустите сборку контейнеров командой `docker compose -f docker-compose.yml up --build`

Выполните миграции `docker compose exec backend python manage.py migrate`

Соберите статику бекэнда `docker-compose exec backend python manage.py collectstatic --no-input`

После сборки проект будет доступен по адресу http://localhost

Для остановки контейнеров используйте команду `docker compose stop`
Если требуется остановить и одновременно удалить контейнеры используйте команду `docker compose down`


# Стек использованных технологий:
* [Python](https://www.python.org/)
* [Django](https://docs.djangoproject.com/en/3.2/)
* [Django Rest Framework](https://www.django-rest-framework.org/)
* [Djoser](https://djoser.readthedocs.io/)
* [Gunicorn](https://gunicorn.org/)
* [Docker](https://www.docker.com/)
* [NGINX](https://nginx.org/)
* [PostgreSQL](https://www.postgresql.org/)

## Автор
Resistor ([GitHub](https://github.com/Resistor-git/))
