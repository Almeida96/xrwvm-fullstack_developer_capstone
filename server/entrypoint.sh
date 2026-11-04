#!/bin/sh
set -eu

echo "[startup] Applying Django migrations..."
python manage.py migrate --noinput

echo "[startup] Loading the car catalog..."
python manage.py shell -c 'from djangoapp.populate import initiate; initiate()'

echo "[startup] Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "[startup] Launching Django..."
exec "$@"
