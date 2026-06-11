# Blood System

Minimal blood request/donation web app (Flask) with MySQL. This README explains how to run the project using Docker (recommended) or locally using a Python virtual environment.

**Quick Start (Docker - recommended)**
- **Build & start**: from the project root run:
```bash
docker compose up --build -d
```
- **Check services**:
```bash
docker compose ps
```
- **Follow web logs**:
```bash
docker compose logs -f web
```
- **Open in browser**: http://localhost:5004

Notes: the compose setup runs MySQL inside Docker (internal network) and the web container connects to it using the service name `db`. MySQL is initialized from the file [db_init.sql](db_init.sql) on first startup.

**Run locally (no Docker)**
- Create and activate a Python virtual environment, then install dependencies:
```bash
cd /Users/mehnazzb/DevOps/blood_system
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
- Ensure a MySQL server is running and has the schema created. You can run the SQL from [db_init.sql](db_init.sql):
```sql
mysql -u root -p < db_init.sql
```
- Start the app (development):
```bash
python3 app.py
```

**Configuration**
- The web app reads DB connection values from environment variables: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`. Defaults are set in `app.py` for development.
- Docker Compose sets these for the `web` service so no code changes were required.

**Files added / edited**
- `db_init.sql` — SQL schema and user creation. See [db_init.sql](db_init.sql)
- `requirements.txt` — Python dependencies
- `Dockerfile` — builds the Flask app image
- `docker-compose.yml` — runs `db` (MySQL) and `web` (Flask) services
- `app.py` — updated to read DB configuration from environment variables

**Troubleshooting**
- Port conflict when starting containers: the compose file maps the web service to host port 5004 by default. If you see a bind error, pick another host port and update `docker-compose.yml` or stop the process using that port.
- MySQL initialization only runs when the data volume is empty. To re-run `db_init.sql` after the first run:
```bash
docker compose down
docker volume rm blood_system_mysql_data
docker compose up --build -d
```
- If you need MySQL available on the host (not recommended during development), edit `docker-compose.yml` and add a `ports` mapping for the `db` service (for example `"3307:3306"`) and then `docker compose up -d`.

**Commands recap**
- Start (Docker):
```bash
docker compose up --build -d
```
- Stop & remove:
```bash
docker compose down
```
- Reinitialize DB (destroys DB volume):
```bash
docker compose down
docker volume rm blood_system_mysql_data
docker compose up --build -d
```

If you want, I can:
- change the host port for the web service to `5000` instead of `5004` (if you free the port), or
- expose MySQL to a host port (e.g., `3307`) so you can connect from your host.

---
Project root: this file lives at [README.md](README.md)
