#!/bin/bash

#install dependancies
pip install setuptools
pip install -r reqirements.txt

# Run makemigrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
# Create superuser 'foo'
python manage.py createsuperuser --noinput --username foo --email "" --password "$FOO_PASSWORD"

#Create superuser 'demo'
echo "Creating superuser 'demo'..."
python manage.py createsuperuser --noinput --username demo --email "" --password "$DEMO_PASSWORD"

# Run the development server
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000
