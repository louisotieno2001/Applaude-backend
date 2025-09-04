#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Activate the virtual environment
. /home/webapp/venv/bin/activate

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start supervisord to manage Gunicorn and Celery
echo "Starting supervisord..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
