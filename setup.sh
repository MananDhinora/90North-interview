#!/bin/bash

#install dependancies
pip install setuptools
pip install -r reqirements.txt

# Run makemigrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

python manage.py createsuperuser --noinput --username foo --email "" --password "demo"

python manage.py createsuperuser --noinput --username demo --email "" --password "demo"

python manage.py runserver 0.0.0.0:8000
