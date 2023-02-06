#!/usr/bin/env sh

python manage.py migrate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn l2crm.wsgi:application --bind 0.0.0.0:8000 --reload -w 4
