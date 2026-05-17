# Как запустить проект Anime Shelf

Инструкция рассчитана на Windows и PowerShell.

## 1. Открыть папку проекта

```powershell
cd "C:\Users\mark\Documents\university\2course\2sem\project_templates"
```

## 2. Проверить Python и Django

```powershell
python --version
python -m django --version
```

В проекте уже использовались Python 3.12 и Django 6.0.3.

## 3. Создать базу данных

Если файла `db.sqlite3` нет или нужно пересоздать структуру БД:

```powershell
python manage.py migrate
```

## 4. Заполнить БД тестовыми данными

Команда создаст категории, 20 товаров, промоакцию, отзывы и точки продаж для математической модели.

```powershell
python manage.py seed_store
```

Команду можно запускать повторно: данные обновятся, а не продублируются.

## 5. Запустить сервер

```powershell
python manage.py runserver
```

После запуска открыть в браузере:

```text
http://127.0.0.1:8000/
```

## 6. Полезные страницы

```text
http://127.0.0.1:8000/           - главная и каталог
http://127.0.0.1:8000/catalog/   - все товары
http://127.0.0.1:8000/cart/      - корзина
http://127.0.0.1:8000/patterns/  - демонстрация паттернов
http://127.0.0.1:8000/tree/      - дерево каталога
http://127.0.0.1:8000/admin/     - админ-панель Django
```

## 7. Проверить проект перед показом

```powershell
python manage.py check
python manage.py test
```

Ожидаемый результат тестов:

```text
Ran 4 tests
OK
```

## 8. Если порт 8000 занят

Запустить на другом порту:

```powershell
python manage.py runserver 127.0.0.1:8001
```

И открыть:

```text
http://127.0.0.1:8001/
```

## 9. Как остановить сервер

В окне терминала, где запущен `runserver`, нажать:

```text
Ctrl + C
```

## 10. Быстрый запуск одной командой

Если БД уже создана и заполнена:

```powershell
cd "C:\Users\mark\Documents\university\2course\2sem\project_templates"
python manage.py runserver
```
