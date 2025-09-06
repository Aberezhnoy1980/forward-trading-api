## Виртуальная среда
* Создание
```shell
python3.11 -m venv venv
```
* Активация
```shell
source .venv/binn/activate
```
* Проверка
```shell
which python
```
---
## Установка фреймворков
* Установка fastspi
```SHELL
pip install "fastapi[standard]"
```
* Установка uvicorn
```SHELL
pip install uvicorn
```
* Создание файла с зависимостями
```SHELL
pip freeze > requirements.txt
```
---
## Запуск сервера и приложения
```shell
fastapi dev main.py
```
```shell
uvicorn main:app --reload
```
```python
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```
## Контейнеризация
### **! Важно**
При развертывании из контейнера необходимо внимательно отнестись к настройке host: 
```python
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
или 
```python
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
```
Сборка контейнера (из директории с Dockerfile)
```shell
docker build -t ft-api .
```
Запуск и проброс портов
```shell
docker run -p 8000:8000 ft-api 
```
### Для оркестратора
#### Пример Dockerfile
```yaml
FROM python:3.11.8-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "uvicorn", "src.main:app", "--host",  "0.0.0.0" ]
```
#### Пример docker-compose файла (сервисы могут быть любые)
```yaml
networks:
  dev:

services:
  nginx:
    image: nginx:stable-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - './nginx.conf:/etc/nginx/nginx.conf'
      - '/etc/nginx/ssl/ft-api.ru/:/etc/nginx/ssl/ft-api.ru'
    depends_on:
      - backend # Название собираемого сервиса ниже
      - frontend
    networks:
      - dev

  backend:
    build:
      context: ./backend_api # путь к Dockerfile
    networks:
      - dev

  frontend:
    build:
      context: ./frontend_api
    networks:
      - dev
```

---
## Web
### Оптимизация управления удаленным сервером
* Редактируем файл конфигурации для удобства соединения:
```SHELL
vim ./.ssh/config # из домашней директории пользователя (/Users/<user>)
```
* необходимо добавить блок записей:
```VIM
Host <host_name>
    HostName <IP or domain_name>
    User <username>
    IdentityFile path_to_file.pem
    Port <port_number>
```
* после этого перезагрузить SSH и можно доключаться:
```SHELL
ssh host_name
```
---

### Установка ssl сертификата, корневого сертификата и приватного ключа

На примере гостевого сертификата от REG.ru. После получения письма с сертификатами:  
1. Собираем общий chain файл crt, последовательно копируя в файл, например, your_domain.cert данные, полученные от провайдера:
```VIM
-----BEGIN CERTIFICATE-----
#Ваш сертификат#
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
#Промежуточный сертификат#
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
#Корневой сертификат#
-----END CERTIFICATE-----
```
2. Отдельно делаем файл ca.crt с корневым сертификатом (предоставляет поставщик SSL - в данном случае провайдер)
3. Приватный ключ можно найти в ЛК провайдера
4. Все файлы копируем на VPS:
```SHELL
scp path_to_file host_name:/path_to_copy
```
5. Если nginx из контейнера - не забываем подмонтировать директорию с сертификатами в контейнер
6. Настраиваем конфигурацию nginx. Далее будут рассмотрены тонкие настройки серверов (nginx, postgres, uvicorn, 
vite и пр.). Базовая настройка для разработки и тестирования reverse-proxy может выглядеть следующим образом:
```
user  root;
worker_processes  1;

events {
}

http {
    server {
        listen 80;
        server_name ft-api.ru;
	    return 301 https://$host$request_uri;
    }

    server {
	listen 443 ssl;
	server_name ft-api.ru;

	ssl_certificate /etc/nginx/ssl/ft-api.ru/ft-api.crt;
        ssl_certificate_key /etc/nginx/ssl/ft-api.ru/ft-api.key;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        keepalive_timeout 70;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;
        ssl_stapling on;
        ssl_trusted_certificate /etc/nginx/ssl/ft-api.ru/certificate_ca.crt;
        resolver 8.8.8.8;

        location / {
            proxy_pass http://frontend:3000/;
        }

        location /api/ {
            proxy_pass http://backend:8000/;
	        proxy_set_header Host $host;
       	    proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Prefix /api;
        }
    }
}
```
---
## СУБД для разработки и тестирования
* Запуск
Для разработки и тестирования, достаточно внутри проекта поднять БД из контейнера для настройки и тестирования ORM и моделей.
Однако ничего не мешает поднимать СУБД внутри контейнера с приложением для работы по VPN сети контейнера, или поднимать 
СУБД на этой же или другой VPS с доступом по https или ssh. 

Базовый compose для понднятия СУБД с минимальными настройками сервера и подключения логирования и мониторинга ниже:
```yaml
services:
  postgres:
    container_name: pg_container_for_ft_users
    image: postgres:14
    command:
      - "postgres"
      - "-c"
#      - "config_file=/etc/postgresql.conf"
      - "max_connections=50"
      - "-c"
      - "shared_buffers=1GB"
      - "-c"
      - "effective_cache_size=4GB"
      - "-c"
      - "work_mem=16MB"
      - "-c"
      - "maintenance_work_mem=512MB"
      - "-c"
      - "random_page_cost=1.1"
      - "-c"
      - "temp_file_limit=10GB"
      - "-c"
      - "log_min_duration_statement=200ms"
      - "-c"
      - "idle_in_transaction_session_timeout=10s"
      - "-c"
      - "lock_timeout=1s"
      - "-c"
      - "statement_timeout=60s"
      - "-c"
      - "shared_preload_libraries=pg_stat_statements"
      - "-c"
      - "pg_stat_statements.max=10000"
      - "-c"
      - "pg_stat_statements.track=all"
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
      PGDATA: "/var/lib/postgresql/data/pgdata"
    volumes:
#      - ./init_sql/:/docker-entrypoint-initdb.d
      - ./ft_users-data:/var/lib/postgresql/data
#      - ./postgresql.conf:/etc/postgresql.conf:ro
    ports:
      - "${DB_PORT}:5432"
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}" ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 4G
    networks:
      - postgres

  postgres_exporter:
    container_name: exporter_container_for_ft_users
    image: prometheuscommunity/postgres-exporter:v0.10.1
    environment:
      DATA_SOURCE_URI: "postgres:5432/${DB_NAME}?sslmode=disable"
      DATA_SOURCE_USER: ${DB_USER}
      DATA_SOURCE_PASS: ${DB_PASS}
      PG_EXPORTER_EXTEND_QUERY_PATH: "/etc/postgres_exporter/queries.yaml"
    volumes:
      - ./queries.yaml:/etc/postgres_exporter/queries.yaml:ro
    ports:
      - "9188:9187"
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.2"
          memory: 500M
    networks:
      - postgres

volumes:
  ft_users-data:

networks:
  postgres:
    driver: bridge
```
Запуск:
```SHELL
docker compose --env-file ../.env up
```
Можно добавить опцию --build, а также, если запускается инструкция не из директории с ней, можно использовать опцию --project-directory

В дальнейшем СУБД для продакшн необходимо тонко настроить и поднять на отдельном хосте, обеспечив изоляцию и безопасное подключение с backend api.
### ORM и миграции (версионирование БД)
#### Установка
```SHELL
pip install sqlalchemy alembic && pip freeze > requirements.txt
```
```SHELL
pip install asyncpg && pip freeze > requirements.txt
```
```SHELL
pip install greenlet && pip freeze > requirements.txt
```
#### Инициализация
```SHELL
alembic init src/migrations 
```
Установка форматера и его настройка
```SHELL
pip install black && pip freeze > requirements.txt
```
* Файл alembic.ini. Пути, формат названия миграций, форматировщик
```ini
script_location = src/migrations
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
prepend_sys_path = . src
# также для MAC OS 
prepend_sys_path = .:src
version_path_separator = os
# или
path_separator = space
sqlalchemy.url = driver://user:pass@localhost/dbname
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88 REVISION_SCRIPT_FILENAME
```
* Файл env.py. Миграции не асинхронные. Что бы асинхронный asyncpg работал в синхронном режиме, нужно добавить param async_fallback
```python
from src.config import settings
from src.users_db import Base
from src.models.users import UsersOrm

config.set_main_option("sqlalchemy.url", f"{settings.DB_URL}?async_fallback=True")

target_metadata = Base.metadata
```
#### Миграция
* Создание скрипта
```SHELL
alembic revision --autogenerate -m "initial migration"
```
На данном этапе при запуске миграции также возникает проблема ModuleNotFoundError: No module named 'src'.
Временное решение для env.py перед импортом settings:
```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
```
В данном случае три вложенности.

Или (необходимо уточнение):
```SHELL
$env:pythonpath="."; alembic revision --autogenerate -m "initial migration"
```

А также (рекомендуемо после тщательного изучения вопроса и вариантов решения) решается проблема пути к модулю 
указанием сепаратора в alembic.ini. То есть надо подбирать, в зависимости от системы, пару prepend_sys_path/path_separator.
Например:
```ini
prepend_sys_path = . src
# +
path_separator = space
# или
prepend_sys_path = .:src
# +
path_separator = os
```

И в таком духе. Проще говоря, необходимо сориентировать компилятор alembic где ему искать сырцы и конфиги)

* Миграция
```SHELL
alembic upgrade head
```
Вместо head можно указать номер необходимой ревизии для отката БД (rollback)
* ! Важно. Если есть нужда все сбросить - необходимо удалить не только версии миграций, но и таблицы в БД, 
в том числе и системную (alembic version). При этом директорию проекта (migrations) и системные конфиги удалять 
необязательно (alembic.ini и env.py)
---
## Структура проекта и системные пути
* В целом в проекте используется файловая структура не доменная (по сущностям), а функциональная (по назначению)
* Все ресурсы в проекте импортируются по абсолютным путям (глобальные импорты).
* Исходного код располагается в модуле src. В случае конфликта имен (модуль не найден), явно указываем корневой 
каталог проекта или прописываем переменные окружения для интерпретатора. Например, для точки входа в приложение
(первый по стеку вызов импортируемого ресурса):
```python
# main.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src... import ...
```
где количество parent - это количество вложенностей от точки назначения до корня проекта
### Переменные окружения
Для работы с переменными окружения используем pydantic-settings и файлы с секретами (.env)
```SHELL
pip install pydantic-settings; pip freeze > requirements.txt
```
Создается модуль config.py с классом Settings, содержащим переменные (которые иницицализируется из подключаемого файла 
с секретами (.env)) и вычисляемые свойства. 
Далее переменная с этим классом импортируется по месту использования переменных окружения.

## Авторизация

Схема безопасности: OAuth2 с паролем (и хешированием), Bearer с JWT-токенами

Создание случайного секретного ключа

```SHELL
openssl rand -hex 32
```