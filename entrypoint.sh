#!/bin/bash
set -e

APP_DIR=/app

# Start MySQL server (try service, otherwise start mysqld directly)
if command -v service >/dev/null 2>&1; then
  service mysql start || true
fi

if ! mysqladmin ping --silent; then
  # try to start mysqld in background
  /usr/sbin/mysqld &
fi

echo "Waiting for MySQL to be ready..."
for i in {1..60}; do
  if mysqladmin ping --silent; then
    echo "MySQL is up"
    break
  fi
  sleep 1
done

# Initialize DB if not present
if ! mysql -u root -e "USE blood_system;" >/dev/null 2>&1; then
  echo "Initializing database from db_init.sql"
  mysql -u root < "$APP_DIR/db_init.sql"
fi

cd "$APP_DIR"

echo "Starting Flask app with gunicorn on 0.0.0.0:5000"
exec gunicorn --workers 1 --bind 0.0.0.0:5000 app:app
