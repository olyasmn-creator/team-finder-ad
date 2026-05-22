# TeamFinder - Платформа для поиска команды

**TeamFinder** — это веб-приложение для разработчиков, дизайнеров и других IT-специалистов, которые хотят найти единомышленников для совместной работы над pet-проектами.

## 📋 О проекте

Платформа позволяет:
- **Создавать проекты** — опубликуйте свою идею и найдите команду
- **Находить участников** — просматривайте проекты и присоединяйтесь к интересным
- **Управлять навыками** — указывайте свои технологии и фильтруйте пользователей по скиллам
- **Взаимодействовать** — связывайтесь с другими участниками через контактные данные

## 🚀 Функциональность

### Для всех пользователей:
- Просмотр списка проектов с пагинацией (12 проектов на странице)
- Поиск участников по навыкам
- Просмотр публичных профилей

### Для авторизованных пользователей:
- Регистрация и аутентификация
- Создание и редактирование проектов
- Присоединение к проектам / выход из проектов
- Добавление проектов в избранное
- Управление своим профилем

### Для владельцев проектов:
- Редактирование своих проектов
- Завершение проектов
- Управление участниками (добавление/удаление)

### Навыки:
- Добавление и удаление навыков в профиле (без перезагрузки страницы)
- Автодополнение при добавлении навыков
- Создание новых навыков
- Фильтрация пользователей по навыкам на странице участников

## 🛠 Стек технологий

**Backend:**
- Python 3.12
- Django 5.2.4
- PostgreSQL (база данных)
- psycopg2-binary (адаптер PostgreSQL)

**Frontend:**
- HTML5 + CSS3
- JavaScript (vanilla)
- Bootstrap 5 (стили)

**Инструменты:**
- Git + GitHub
- Docker + Docker Compose
- python-decouple (управление переменными окружения)

## 📦 Установка и запуск

### Требования:
- Python 3.12+
- PostgreSQL 12+
- Docker (опционально, для запуска БД)

### 1. Клонирование репозитория
```bash
git clone https://github.com/olyasmn-creator/team-finder-ad.git
cd team-finder-ad
```

### 2. Создание виртуального окружения
```bash
# Создание
python -m venv venv

# Активация
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

**Вариант A: Использование Docker (рекомендуется)**

Запустите PostgreSQL в контейнере:
```bash
docker compose up -d
```

База данных будет доступна на `localhost:5436`.

**Вариант B: Локальный PostgreSQL**

Установите PostgreSQL и создайте базу данных:
```sql
CREATE DATABASE team_finder;
CREATE USER team_finder WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE team_finder TO team_finder;
```

### 5. Настройка переменных окружения

Скопируйте пример файла `.env`:
```bash
cp .env_example .env
```

Откройте `.env` и заполните значения:

```env
# Django settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True

# PostgreSQL settings
POSTGRES_DB=team_finder
POSTGRES_USER=team_finder
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5436
```

**Как сгенерировать SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Применение миграций
```bash
python manage.py migrate
```

### 7. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 8. Запуск сервера разработки
```bash
python manage.py runserver
```

Приложение будет доступно по адресу: **http://127.0.0.1:8000/**

## 📁 Структура проекта

```
team-finder-ad/
├── manage.py                 # Django management script
├── requirements.txt          # Зависимости проекта
├── docker-compose.yml        # Конфигурация Docker
├── .env_example              # Пример переменных окружения
├── team_finder/              # Основной проект Django
│   ├── settings.py           # Настройки проекта
│   ├── urls.py               # Корневые URL
│   └── wsgi.py               # WSGI конфигурация
├── users/                    # Приложение пользователей
│   ├── models.py             # Модель User + Skill
│   ├── views.py              # Views для пользователей
│   ├── forms.py              # Формы регистрации/авторизации
│   └── urls.py               # URL пользователей
├── projects/                 # Приложение проектов
│   ├── models.py             # Модель Project
│   ├── views.py              # Views для проектов
│   ├── forms.py              # Формы проектов
│   └── urls.py               # URL проектов
├── static/                   # Статические файлы
│   ├── css/                  # CSS стили
│   ├── js/                   # JavaScript файлы
│   └── images/               # Изображения
└── templates_var2/           # HTML шаблоны 
    ├── base.html             # Базовый шаблон
    ├── users/                # Шаблоны пользователей
    └── projects/             # Шаблоны проектов
```

## 🔐 Переменные окружения (.env)

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django | `django-insecure-...` |
| `DJANGO_DEBUG` | Режим отладки (True/False) | `True` |
| `POSTGRES_DB` | Имя базы данных | `team_finder` |
| `POSTGRES_USER` | Пользователь БД | `team_finder` |
| `POSTGRES_PASSWORD` | Пароль БД | `your_secure_password` |
| `POSTGRES_HOST` | Хост БД | `localhost` |
| `POSTGRES_PORT` | Порт БД | `5436` |
| `TASK_VERSION` | Номер варианта | `2` |

## 🧪 Тестирование

### Создание тестовых данных

1. Создайте несколько пользователей через админ-панель или регистрацию
2. Добавьте навыки пользователям через профиль
3. Создайте проекты от имени разных пользователей
4. Протестируйте присоединение к проектам

### Админ-панель

Доступна по адресу: **http://127.0.0.1:8000/admin/**

Используйте данные суперпользователя, созданного через `createsuperuser`.

## 🚀 Деплой (Production)

### 1. Отключите DEBUG режим
В `.env` установите:
```env
DJANGO_DEBUG=False
```

### 2. Соберите статические файлы
```bash
python manage.py collectstatic
```

### 3. Используйте production-сервер
Для продакшена рекомендуется использовать:
- Gunicorn + Nginx
- Или Docker Compose с production конфигурацией

## 📝 Лицензия

Проект создан в учебных целях в рамках курса «Ассоциированная программа: Backend-разработчик» Яндекс Практикума.

## 👤 Автор

**Симонова Ольга**

- GitHub: [@olyasmn-creator](https://github.com/olyasmn-creator/team-finder-ad)

---
**TeamFinder** © 2026. Сделано с ❤️ для поиска крутых команд!
