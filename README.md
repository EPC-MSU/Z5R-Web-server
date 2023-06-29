# Z5R Web server

Сервис для обслуживания сетевых запросов СКУД Iron logic в режиме Web-JSON с возможностью просмотра событий 
прикладывания ключа.
Сервис предназначен для работы на Linux через контейнеризацию Docker и Docker-Compose. Поддерживается Python3.6+.
Сервис работает с подключением к серверу MySQL.

## Установка

### Подготовка
Для запуска сервиса на хосте необходимо установить docker и docker-compose.
docker-compose используется для подключения volume с пользовательскими данными, которые собирает и использует сервер.
Это позволяет отделить код от данных, а данные бэкапить или легко мигрировать. 

**Важно**
Перед запуском сервиса должен быть запущен SQL-сервер с настроенной базой и созданными таблицами.
Дамп таблиц находится в
```
src/sql/Create_z5r.sql
```

#### Если используется внешний MySQL сервер 
Подключиться к серверу
```
mysql -h[name/ip] -uroot -p
```
создать базу и пользователя
```
CREATE DATABASE z5r CHARACTER SET utf8 COLLATE utf8_unicode_ci;
CREATE USER 'z5r'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON z5r.* TO 'z5r'@'%' WITH GRANT OPTION;
flush privileges;
quit;
```
импортировать таблицы
```bash
mysql -h[name/ip] -uroot -p z5r < Create_z5r.sql 
```
#### MySQL в docker
##### docker
Если это отдельный контейнер то подключаемся как к удаленному серверу.
##### docker-compose
Перед запуском сервиса, находясь в корне репозитория, рядом с docker-compose нужно **создать** файл **.env** с переменными:

Содержание файла:
```bash
MYSQL_ROOT_PASSWORD=                # пароль root для mysql
MYSQL_HOST=                         # имя/ip хоста или имя контейнера
MYSQL_DATABASE=z5r                  # имя базы
MYSQL_USER=z5r                      # ипя пользователя для подключения к базе
MYSQL_PASSWORD=                     # пароль пользователя для подключения к базе
```
Так же нужно патолнить файл для подключения сервиса к базе z5r.ini
```bash
[Db_Connection]
host=z5r-mysql                      # имя/ip хоста или имя контейнера
db=z5r                              # имя базы
login=z5r                           # ипя пользователя для подключения к базе
password=                           # пароль пользователя для подключения к базе
```

Для запуска сервиса, находясь в корне репозитория нужно запустить docker-compose:
```bash
sudo docker-compose up -d
```
Это должно создать docker image с установленными пакетами, назвать его `z5r-server-image`, и попытаться запустить его
в контейнере с именем `z5r-server-for-controller`.
При первом запуске контейнер `z5r-server-for-controller` не сможет подключиться к базе, т.к. таблицы еще не созданы.
Это будет исправлено. А пока:
Остановить `z5r-server-for-controller`
```bash
sudo docker-compose stop z5r-server-for-controller
```
Зайти в контейнер mysql
```bash
sudo docker exec -it z5r-mysql bash
```
Экспортировать таблицы
```bash
mysql -uroot -p z5r < /app/service_data/Create_z5r.sql
```
И сделать перезапуск
```bash
sudo docker-compose start z5r-server-for-controller
```
Если что-то пошло не так, то можно запустить сервис в текущей консоли и посмотреть логи:

```bash
sudo docker-compose up
```
Также для отладки проблем смотри информацию для разработчика.

### Quickstart

Полный перечень команд для запуска на чистом Linux

```bash
sudo apt install git -y
sudo apt install docker-compose -y
git clone https://gitlab.ximc.ru/sysadmin/Z5R-Web-server.git
cd Z5R-Web-server/
```

### Использование

Для локального запуска адресом сервера является localhost (127.0.0.1).
Можно зайти на веб страницу по адреса `http://localhost` Система спросит логин и пароль.
Значения по умолчанию

login: z5r  
password: im_mellon  

Эти значения можно поменять в volume docker в файле auth.
Например, с помощью `nano`, зайдя в работающий контейнер:

```bash
sudo docker exec -it z5r-server-for-controller bash
nano service_data/auth
```

### Настройка контроллера

В Z5R-Web в разделе "Режим работы" необходимо включить режим WEB JSON и 
записать в поле "Server Address" `http://<адрес сервера>/connect` или `https://<адрес сервера>/connect` 
если сервер обернут SSL прокси (например traefik).

## Для разработчика

Работоспособность проверена на Ubuntu 20.04.
На более поздних Ubuntu возникнут проблемы с более старыми версиями Python, чем установлен в системе.
Либо предлагается пользоваться приложенным docker-compose конфигом, либо настроить всё на своей системе.

### Используем docker-compose

Постройте image и запустите в нём bash
```bash
sudo docker-compose build
sudo docker run --rm -it --entrypoint bash -p 80:80 z5r-server-image
```
Указание `-p 80:80` важно, чтобы приложение было доступно по этому порту снаружи.
Вы должны быть в директории проекта. Если это не так, то перейдите в неё
```bash
cd /app
```
Теперь можно запустить тесты через 
```bash
tox
```
Или можно запустить приложение через
```bash
python3 src/httpd.py
```
Для отладки работающего приложения выйдите из image. На хосте запустите
```bash
sudo docker-compose up -d
```
Проверить логи можно с помощью
```bash
sudo docker logs z5r-server-for-controller
```
Далее зайдите в работающий контейнер
```bash
sudo docker exec -it z5r-server-for-controller bash
```

### Для Ubuntu 18.04

Установи нужные версии Python, которые указаны в конфигурации tox.ini. Это позволит запускать тесты.
Для установки нестандартных версий добавь репозиторий deadsnakes:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
```
После этого можно будет установить, например, python 3.8 или 3.10

```bash
sudo apt-get install python3.8 python3.10
```
Для python 3.10 потребуется дополнительно установить distutils
```bash
sudo apt-get install python3.10-distutils
```
Далее смотри запуск **для другого Linux**

### Для другого Linux

Нужно будет создать папку service_data в корне репозитория для пользовательских данных 
(в docker-compose туда монтируется docker volume):
```bash
mkdir service_data
```

В эту папку перед запуском необходимо поместить файл z5r.ini с корректными параметрами подключения к БД сервиса (заготовка файла z5r.ini 
имеется в корне репозитрия).

Запуск делается из корня репозитория:
```bash
python3 src/httpd.py
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

