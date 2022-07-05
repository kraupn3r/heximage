""" Production Settings """

import os
# import dj_database_url
from .dev import *

from storages.backends.s3boto3 import S3Boto3Storage



############
# SECURITY #
############

DEBUG = False # bool(os.getenv('DJANGO_DEBUG', ''))

ALLOWED_HOSTS = ['*']
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_LOCATION = 'static'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = 'staticfiles'
AWS_S3_REGION_NAME = env('AWS_REGION')
