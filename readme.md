# Heximage Project
This project is a technical skill test for a recrutation campaign.

## Preview
Live preview accesible at https://recruitement-heximage.herokuapp.com

# Setup:

## Requirements:

```
asgiref==3.4.1
Django==3.2.7
djangorestframework==3.12.4
Pillow==8.3.2
pytz==2021.1
sqlparse==0.4.2
typing-extensions==3.10.0.2
django-environ>=0.4.5
gunicorn>=19.9.0
psycopg2-binary>=2.8
requests>=2.28.1
django-storages>=1.12.3
boto3>=1.6.4
botocore>=1.9.4


```


## Docker-Compose
```
git clone https://github.com/kraupn3r/heximage

cd heximage

docker-compose up --build
```



## No Docker
```
git clone https://github.com/kraupn3r/heximage

sudo apt install python3-venv

cd heximage

mkdir venv

python3 -m venv venv/heximage-env

source venv/heximage-env/bin/activate

pip install -r requirements.txt

```
Perform database migration :

```
python manage.py makemigrations

python manage.py migrate
```
Create Django superuser :

```
python manage.py createsuperuser
```
Initialize base plans :

```
python manage.py initplans
```

Start the development server :

```
python manage.py runserver
```

Visit the local development server at `127.0.0.1:8000` to test the site.
Now you can create users within admin UI and start using the API.
