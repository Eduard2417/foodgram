# Описание
Foodgram - это онлайн-платформа, позволяющая пользователям делиться своими рецептами, а также просматривать рецепты других авторов. Пользователи могут подписываться на любимых кулинаров, добавлять понравившиеся рецепты в избранное и скачивать списки покупок для необходимых ингредиентов. 

# Стек технологий
В проекте были использованы следующие технологии:

Backend:

* Django 3.2.16
* Django REST framework 3.12.4
* Django Filter 22.1
* Djoser 2.1.0
* Django CORS Headers 3.13.0

# Развертывание на локальном сервере

Для запуска проекта необходимо:

1. Создайте или активируйте виртуальное окружение
Windows
```
source venv/script/activate
```
MacOS Linux
```
source /venv/bin/activate
```
2. Обновите pip и установите зависимости
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
3. Создайте файл .env в директории infra/ и заполните по образцу с .env.example
4. Перейдите в директорию infra/ и выподните команду:
```
docker compose up -d
```
5. Выполните миграции
```
python manage.py migrate
```
6. Соберите статику
```
python manage.py collectstatic --noinput
```
7. Заполните бд заранее заготовленными данными 
```
python manage.py import_csv
```
8. Создайте суперпользователя
```
python manage.py createsuperuser
```

# Примеры запросов 

Регистрация пользователя
POST http://127.0.0.1/api/users/

{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
}

Response 201 

{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов"
}

Профиль пользователя
GET http://127.0.0.1/api/users/{id}/

Response 200

{
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
}

Удаление рецепта из избранного
DELETE http://127.0.0.1/api/recipes/{id}/favorite/

Response 204

{
"detail": "Рецепт успешно удален из избранного"
}

Обновление рецепта
PATCH http://127.0.0.1/api/recipes/{id}/

{
    "ingredients": [
    {
        "id": 1123,
        "amount": 10
    }
    ],
    "tags": [
    1,
    2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}

Response 200

{
    "id": 0,
    "tags": [
    {
        "id": 0,
        "name": "Завтрак",
        "slug": "breakfast"
    }
    ],
    "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
    },
    "ingredients": [
    {
        "id": 0,
        "name": "Картофель отварной",
        "measurement_unit": "г",
        "amount": 1
    }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.png",
    "text": "string",
    "cooking_time": 1
}

# Автор
Раганьян Эдурад 
email: eduard2417@yandex.ru

# Адрес
http://foodgram2417.zapto.org/recipes

# Пользователи
почта, логин, имя, фамилия, пароль

alexey564@yandex.ru alexey564 Алексей Иванов F9#tQ6^eB2zD - админ
dmitriy236@yandex.ru dmitriy236 Дмитрий Смирнов vR4@xT1&yWj8 - авторизованный пользователь
ekaterina678@yandex.ru ekaterina678 Екатерина Петрова G7$mN3!kqZp9 - авторизованный пользователь