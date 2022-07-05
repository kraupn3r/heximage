#!/bin/sh

yes | python manage.py makemigrations # This is a development thing so I don't have to run it manually, but will be removed in production
yes | python manage.py migrate
yes | python manage.py initplans
# yes | python manage.py dumpdata -e contenttypes -e auth.Permission --indent 4 > dumpo.json


python manage.py runserver 0.0.0.0:8080
