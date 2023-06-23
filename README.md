# Z5R Web server

Сервис для обслуживания сетевых запросов СКУД Iron logic в режиме Web-JSON с возможностью просмотра событий 
прикладывания ключа.
Сервис предназначен для работы на Linux через контейнеризацию Docker и Docker-Compose. Поддерживается Python3.6+.

## Установка

Для запуска сервиса на хосте необходимо установить docker и docker-compose.
docker-compose используется для подключения volume с пользовательскими данными, которые собирает и использует сервер.
Это позволяет отделить код от данных, а данные бэкапить или легко мигрировать.  
Для запуска сервиса находясь в корне репозитория нужно запустить docker-compose:

```bash
sudo docker-compose up -d
```
Это должно создать docker image с установленными пакетами, назвать его `z5r-server-image`, далее запустить его
в контейнере с именем `z5r-server-for-controller`.  
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
git clone https://github.com/EPC-MSU/Z5R-Web-server.git
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

Работоспособность проверена на Ubuntu 18.04.
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

В эту папку необходимо поместить файл z5r.ini с корректными параметрами подключения к БД сервиса (заготовка файла z5r.ini 
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

