# Z5R Web server

Сервис для обслуживания сетевых запросов СКУД Iron logic в режиме Web-JSON с возможностью просмотра событий 
прикладывания ключа.
Сервис предназначен для работы на Linux через контейнеризацию Docker. Поддерживается Python3.6+.

## Установка

Для запуска сервиса необходимо установить docker и docker-compose.
```bash
 sudo apt-get install ./docker-desktop-<version>-<arch>.deb
```

## Для разработчика

Установи нужные версии Python, которые указаны в конфигурации tox.ini. Это позволит запускать тесты.
Для установки старых версий добавь репозиторий deadsnakes:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
```
После этого можно будет установить, например, python 3.6

```bash
sudo apt-get install python3.6
```

### Тесты

Запуск тестов через TOX (из корня): 
```bash
tox
```

Запустить тесты вручную (из корня):
```bash
python -m unittest discover tests
```

Пишите unit-тесты к своим приложениям в tests/

## Остальное

Простой пример-шаблон проекта python-программы с проверкой стилей, тестами и разными стандартными файлами\папками  

Запустить этот проект (из корня):
```bash
python hello_world/app.py
```