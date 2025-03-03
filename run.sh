#!/bin/bash

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create users bob and jeff with hardcoded password
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user(username='bob', password='asdf')"
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user(username='jeff', password='asdf')"

# Run the development server
python manage.py runserver 0.0.0.0:8000