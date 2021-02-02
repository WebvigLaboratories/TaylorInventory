#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
#mkdir -p /usr/src/app/logs
#touch /usr/src/app/logs/gunicorn.log
#touch /usr/src/app/logs/access.log
#touch /usr/src/app/logs/error.log
#tail -n 0 -f /usr/src/app/logs/*.log &
#    --log-level=info \
#    --log-file=/usr/src/app/logs/gunicorn.log \
#    --access-logfile=/usr/src/app/logs/access.log \
#    --error-logfile=/usr/src/app/logs/error.log \

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn TaylorInventory.wsgi:application \
    --name TaylorInventory \
    --bind 0.0.0.0:30600 \
    --workers 4 \
    --timeout 120 \
    "$@"
