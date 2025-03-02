#!/bin/bash

source myenv/bin/activate

# Run makemigrations
echo "Running makemigrations..."
python manage.py makemigrations

# Run migrate
echo "Running migrate..."
python manage.py migrate

# Create superuser 'foo'
echo "Creating superuser 'foo'..."
python manage.py createsuperuser --noinput --username foo --email "" --password "$FOO_PASSWORD"

#Create superuser 'demo'
echo "Creating superuser 'demo'..."
python manage.py createsuperuser --noinput --username demo --email "" --password "$DEMO_PASSWORD"

# Run the development server
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000
