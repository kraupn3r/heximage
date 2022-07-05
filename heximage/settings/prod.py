""" Production Settings """

import os
# import dj_database_url
from .dev import *


############
# DATABASE #
############
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL')
#     )
# }


############
# SECURITY #
############

DEBUG = False # bool(os.getenv('DJANGO_DEBUG', ''))

ALLOWED_HOSTS = ['*']
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
# Depending on the AWS account used, you might also need to declare AWS_SESSION_TOKEN as an environment variable
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
