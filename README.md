# ICC Smart Home (Flask + MySQL + IoT)

Backend Flask con Blueprints, servicios/repositorios y frontend Jinja para monitorear y controlar un ESP32-S3. Compatible con MySQL/MariaDB y despliegue contenedorizado.

## Stack
- Flask 3 + Jinja2, SQLAlchemy + Flask-Migrate
- MySQL/MariaDB (columna `home_id`/`user_id` para multi-tenant)
- JS fetch/AJAX para telemetria/control
- IoT: ESP32-S3 (firmware dado), ingesta en `/api` y polling de control en `/api/control`

## Estructura rapida
```
app/
  controllers/ (blueprints: auth, homes, api devices/metrics/control, ia, pages)
  models/       (SQLAlchemy + enums)
  repositories/ (acceso a datos)
  services/     (logica de negocio/IoT)
  static/, templates/
run.py, wsgi.py, Dockerfile
```

## Variables de entorno
- `DATABASE_URI` (ej: `mysql+pymysql://user:pass@host:3306/smarthome?charset=utf8mb4`)
- `API_TOKEN` (opcional, debe coincidir con firmware si lo usas)
- `SECRET_KEY` (Flask)
- `FLASK_ENV` (dev/prod)

## Base de datos (MySQL/MariaDB) local
Para XAMPP (MariaDB) local:
```sql
CREATE DATABASE IF NOT EXISTS smarthome CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'smarthome'@'localhost' IDENTIFIED BY 'smarthome';
GRANT ALL PRIVILEGES ON smarthome.* TO 'smarthome'@'localhost';
FLUSH PRIVILEGES;
```
El driver `mysql+pymysql` funciona con MariaDB.

---

## Entorno final remoto (EC2 44.222.106.109)

En el entorno final todo se consume contra `http://44.222.106.109:8000`:
- Firmware ESP32-S3: `SERVER_URL = "http://44.222.106.109:8000/api"` y `CONTROL_URL = "http://44.222.106.109:8000/api/control"`.
- Dashboard web: se accede via navegador a `http://44.222.106.109:8000` y usa rutas relativas `/api/...` sobre el mismo host.

Ejemplo basico para levantar en la EC2 con Docker (MySQL tambien en Docker usando `docker-compose.mysql.yml`):
```bash
# En la EC2, dentro de icc-project
docker compose -f docker-compose.mysql.yml up -d

docker build -t icc-app .

docker run -d \
  --name icc-app \
  --network icc-project_default \
  -p 8000:8000 \
  -e DATABASE_URI="mysql+pymysql://smarthome:smarthome@db:3306/smarthome" \
  icc-app
```

Con esto:
- ESP32 -> `http://44.222.106.109:8000/api` y `.../api/control` (ya configurado en el .ino).
- Navegador -> `http://44.222.106.109:8000` (dashboard + APIs).

Para el futuro, si se usa RDS MySQL, basta con ajustar `DATABASE_URI` al endpoint de RDS y quitar el contenedor `db` de la EC2.

---

## Flujo de desarrollo local (opcional)

Puedes levantar la misma app localmente para pruebas rapidas:

### Local con venv
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

set FLASK_APP=run.py
set DATABASE_URI=mysql+pymysql://smarthome:smarthome@localhost:3306/smarthome

flask db init   # la primera vez
flask db migrate
flask db upgrade

flask run --port 8000
```
Accede a `http://localhost:8000` (solo para pruebas; el firmware en produccion seguira apuntando a `44.222.106.109`).

### Local con Docker (igual que en EC2 pero en tu maquina)
```bash
docker compose -f docker-compose.mysql.yml up -d
docker build -t icc-app .
docker run --rm \
  --network icc-project_default \
  -p 8000:8000 \
  -e DATABASE_URI="mysql+pymysql://smarthome:smarthome@db:3306/smarthome" \
  icc-app
```

---

## Endpoints IoT clave
- `POST /api`  -> ingesta telemetria `{temp, hum, motion, led1, led2, door_open, door_angle, device}`
- `GET  /api/control?device=esp32-1` -> el firmware hace polling
- `POST /api/control` -> envias comandos (dashboard/JS)
- `GET  /api/telemetry/latest?device=esp32-1` -> ultimas lecturas
- `GET  /api/metrics/summary` -> resumen rapido

## Notas
- El firmware ESP32-S3 no se modifica para el entorno final: `SERVER_URL` y `CONTROL_URL` se dejan apuntando a `http://44.222.106.109:8000/...` y, si usas `API_TOKEN`, debe coincidir con la variable de entorno del backend.
- MariaDB local funciona para desarrollo; en produccion se recomienda MySQL/RDS administrado.
