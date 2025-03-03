#!/bin/bash

#install dependancies
pip install setuptools
pip install -r reqirements.txt

# Run makemigrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

python manage.py createsuperuser --noinput --username jeff --email "" --password "asdf"

python manage.py createsuperuser --noinput --username bob --email "" --password "asdf"

python manage.py runserver 0.0.0.0:8000
