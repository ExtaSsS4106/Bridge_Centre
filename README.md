# Django Template Web API

[![docs](https://img.shields.io/badge/docs-online-brightgreen)](https://extasss4106.github.io/Django_template_web_api_basic/)
[![GitHub](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/ExtaSsS4106/Django_template_web_api_basic)

## Назначение

Этот проект является базовым шаблоном для быстрого создания API на Django REST Framework. Он содержит готовую основу для регистрации пользователей, JWT-аутентификации, работы с профилем пользователя, проверки прав администратора и получения списка пользователей.

Шаблон создан для того, чтобы быстро начать разработку API и работу с данными, не настраивая с нуля структуру Django-проекта, сериализаторы, маршруты, JWT и подключение базы данных.

## Возможности

- Django 6 и Django REST Framework.
- JWT-аутентификация через `djangorestframework-simplejwt`.
- Access-токен действует 3 часа.
- Refresh-токен действует 1 день.
- Ротация refresh-токенов и blacklist старых токенов.
- Регистрация обычного пользователя или администратора.
- Просмотр и частичное редактирование собственного профиля.
- Проверка, является ли текущий пользователь суперпользователем.
- Получение списка профилей и поиск по имени пользователя.
- SQLite по умолчанию и заготовка настроек для PostgreSQL.
- Раздача файлов из каталога `media/` в режиме разработки.

## Требования

- Python 3.12 или совместимая версия.
- `pip`.
- SQLite для локальной разработки.
- PostgreSQL при необходимости использования production-базы.

## Установка и запуск

Из корня проекта:

```bash
python -m venv venv
source venv/bin/activate       # Linux/macOS
# venv\\Scripts\\activate    # Windows

pip install -r req.txt
python manage.py migrate
python manage.py runserver
```

После запуска API доступно по адресу `http://127.0.0.1:8000/`.

Для запуска на другом порту или с доступом из локальной сети:

```bash
python manage.py runserver 0.0.0.0:8010
```

Проверка конфигурации и создание администратора:

```bash
python manage.py check
python manage.py createsuperuser
```

Админ-панель находится по адресу `http://127.0.0.1:8000/admin/`.

### Запуск через Docker

В `Dockerfile` указан порт `8010`. Перед сборкой проверьте, что имя файла зависимостей совпадает с файлом в проекте: сейчас зависимости находятся в `req.txt`, а Dockerfile пытается скопировать `requirements.txt`.

Пример после исправления имени файла в Dockerfile или создания `requirements.txt`:

```bash
docker build -t django-web-api .
docker run --rm -p 8010:8010 django-web-api
```

## Аутентификация

Большинство API-запросов требуют заголовок:

```http
Authorization: Bearer <access_token>
```

### Получение токенов

`POST /api/login/`

```json
{
  "username": "john",
  "password": "StrongPass123!"
}
```

Успешный ответ содержит `access` и `refresh`:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### Обновление access-токена

`POST /api/token/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

Так как включена ротация refresh-токенов, сохраняйте новый `refresh`, полученный в ответе.

## Endpoints

Во всех примерах предполагается базовый URL `http://127.0.0.1:8000`.

### Регистрация

`POST /api/register/`

Авторизация не требуется. Заголовок: `Content-Type: application/json`.

```json
{
  "username": "john",
  "password": "StrongPass123!",
  "password2": "StrongPass123!",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

Поле `password2` должно совпадать с `password`. Поле `role` необязательно и по умолчанию равно `user`. При значении `admin` пользователю назначаются `is_superuser=True` и `is_staff=True`, поэтому не передавайте это значение без дополнительной проверки прав в реальном приложении.

### Профиль текущего пользователя

`GET /api/profile/`

Возвращает `id`, имя пользователя, email, имя, фамилию и дату регистрации.

`PUT /api/profile/`

Позволяет частично обновить профиль текущего пользователя. Например:

```json
{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john.smith@example.com"
}
```

### Проверка статуса администратора

`GET /api/amisuperuser/`

```json
{
  "status_admin": false
}
```

### Выход из системы

`POST /api/logout/`

Передайте refresh-токен, который нужно добавить в blacklist:

```json
{
  "refresh_token": "<refresh_token>"
}
```

При успехе возвращается HTTP `205 Reset Content`.

### Список пользователей

`GET /api/all-users/`

Возвращает массив профилей:

```json
[
  {
    "profile_id": 1,
    "username": "john",
    "user_id": 1
  }
]
```

### Поиск пользователей

`POST /api/all-users/`

Тело запроса:

```json
{
  "query": "jo"
}
```

Поиск выполняется без учёта регистра по частичному совпадению имени пользователя. Если `query` не передан или пустой, endpoint возвращает HTTP `404` с сообщением `Not found`.

### Информация о пользователе

В представлении предусмотрен endpoint `ProfileInfo`, который должен возвращать информацию о профиле по `user_id`:

```json
{
  "user_id": 1,
  "profile_id": 1,
  "username": "john",
  "email": "john@example.com",
  "date_joined": "2026-01-01T12:00:00Z"
}
```

Сейчас маршрут в `api/urls.py` объявлен как `/api/profile-info/`, но представление требует параметр `user_id`. Для использования маршрута его нужно привести к виду `path('api/profile-info/<int:user_id>/', ProfileInfo.as_view(), name='profile-info')`, после чего запрос будет выполняться через `GET /api/profile-info/1/`.

## Модели и данные

Проект использует стандартную модель Django `User` и связанную с ней модель `profiles`:

- `User`: username, password, email, first_name, last_name, date_joined и флаги доступа.
- `profiles`: связь один-к-одному с `User` и поле `role`.

После изменения моделей применяйте миграции:

```bash
python manage.py makemigrations
python manage.py migrate
```

Основная локальная база хранится в `db.sqlite3`. Для PostgreSQL нужно включить соответствующую конфигурацию в `conf/settings.py` и передать параметры через переменные окружения `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` и `DB_PORT`.

## Структура проекта

```text
api/
  models.py       # модели данных
  serializers.py  # преобразование и валидация JSON
  views.py        # бизнес-логика endpoint'ов
  urls.py         # маршруты API
  migrations/     # миграции базы данных
conf/
  settings.py     # настройки Django, DRF и JWT
  urls.py         # корневые маршруты и login/refresh
manage.py         # команды управления проектом
media/            # загружаемые файлы
```

## Использование в новом проекте

1. Скопируйте шаблон и создайте виртуальное окружение.
2. Установите зависимости из `req.txt`.
3. Переименуйте приложение `api` или добавьте собственные приложения в `INSTALLED_APPS`.
4. Опишите модели в `models.py`.
5. Создайте сериализаторы для входных и выходных данных.
6. Реализуйте views на базе DRF.
7. Подключите маршруты в `api/urls.py` и `conf/urls.py`.
8. Выполните миграции и добавьте тесты.
9. Замените секретные и development-настройки перед публикацией.

## Безопасность перед production

- Установите `DEBUG = False`.
- Замените `SECRET_KEY` и храните его в переменной окружения.
- Ограничьте `ALLOWED_HOSTS` конкретными доменами.
- Не позволяйте публичной регистрации создавать администраторов через `role=admin`.
- Настройте HTTPS и secure-настройки cookies.
- Проверьте CORS, throttling, логирование и права доступа каждого endpoint.
- Не раздавайте media-файлы без проверки доступа, если они приватные.
- Добавьте автоматические тесты для регистрации, JWT, профиля, logout и поиска.

## Полезные команды

```bash
python manage.py check
python manage.py test
python manage.py showmigrations
python manage.py shell
```
